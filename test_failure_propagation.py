"""
test_failure_propagation.py
===========================
Deterministic failure-path integration test for Riya v2.

Strategy
--------
* Monkey-patches `search_youtube.execute` to raise an intentional exception.
  No source file is permanently modified.
* Drives the full runtime pipeline (workflow_manager + task_manager +
  orchestrator + event_bus) the same way core/main.py does.
* Subscribes lightweight listeners that record every event emission.
* After the run, asserts every required invariant and prints a structured
  execution trace + verdict.

Run:
    python test_failure_propagation.py
"""

import sys
import unittest

# ---------------------------------------------------------------------------
# 0. IMPORT ORDER MATTERS — subscribers are registered on import
# ---------------------------------------------------------------------------
import riya_engine.runtime.runtime_subscribers   # registers TASK_* handlers
import riya_engine.runtime.debug_subscriber       # optional, already live

from riya_engine.runtime.event_bus       import event_bus
from riya_engine.runtime.event_types     import (
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED,   STEP_COMPLETED,   STEP_FAILED,
)
from riya_engine.runtime.task_manager    import task_manager
from riya_engine.runtime.orchestrator    import orchestrator
from riya_engine.workflows.workflow_manager import workflow_manager
from riya_engine.state.runtime_state     import runtime_state

# Capability we will intentionally break
import riya_engine.capabilities.search_youtube as search_youtube_mod
from riya_engine.capabilities.registry import CAPABILITY_REGISTRY


# ===========================================================================
# SECTION 1 — Event tracker
# ===========================================================================

class EventTracker:
    """Records every (event_name, data) pair emitted during the test."""

    def __init__(self):
        self.log = []            # list of (event_name, data)
        self._counts = {}        # event_name -> int

    def listener(self, event_name):
        def _handler(data):
            self.log.append((event_name, data))
            self._counts[event_name] = self._counts.get(event_name, 0) + 1
        _handler.__name__ = f"tracker_{event_name}"
        return _handler

    def count(self, event_name):
        return self._counts.get(event_name, 0)

    def was_emitted(self, event_name):
        return self._counts.get(event_name, 0) > 0

    def dump_trace(self):
        print("\n" + "=" * 60)
        print("FULL EXECUTION TRACE")
        print("=" * 60)
        for i, (name, data) in enumerate(self.log, 1):
            print(f"  [{i:02d}] {name}")
            if isinstance(data, dict):
                for k, v in data.items():
                    if k not in ("steps",):   # skip noisy nested lists
                        print(f"         {k}: {v}")
        print("=" * 60)


tracker = EventTracker()

# Subscribe tracker to every event we care about
for evt in [
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED, STEP_COMPLETED, STEP_FAILED,
]:
    sub = tracker.listener(evt)
    event_bus.subscribe(evt, sub)


# ===========================================================================
# SECTION 2 — Monkey-patch: inject guaranteed failure
# ===========================================================================

INJECTED_ERROR = "Intentional workflow failure test"

_original_execute = search_youtube_mod.execute

def _failing_execute(payload):
    raise Exception(INJECTED_ERROR)

# Patch both the module attribute AND the registry entry
search_youtube_mod.execute = _failing_execute
CAPABILITY_REGISTRY["search_youtube"] = _failing_execute

print("\n[PATCH] search_youtube.execute replaced with failing stub.")


# ===========================================================================
# SECTION 3 — Build a minimal single-step workflow (mirrors core/main.py)
# ===========================================================================

CAPABILITY   = "search_youtube"
PAYLOAD      = {"query": "failure test video"}
FAKE_INTENT  = "SEARCH_YOUTUBE"
PLAN         = [{"step": 1, "capability": CAPABILITY, "payload": PAYLOAD}]

workflow = workflow_manager.create_workflow(FAKE_INTENT, PLAN)
workflow_id = workflow["workflow_id"]

print(f"\n[SETUP] Workflow created  — id={workflow_id}")
print(f"        Active workflows   : {list(workflow_manager.active_workflows.keys())}")


# ===========================================================================
# SECTION 4 — Execute (mirrors core/main.py lines 129-213)
# ===========================================================================

workflow_manager.start_workflow(workflow)
event_bus.emit(WORKFLOW_STARTED, workflow)

print("\n[RUNNING] Executing workflow steps...\n")

step_failed_flag = False

for step in workflow["steps"]:

    try:
        # --- STEP START ---
        workflow_manager.start_step(workflow, step["step"])
        event_bus.emit(STEP_STARTED, step)

        task = task_manager.create_task(step["capability"], step["payload"])
        task["workflow_id"] = workflow_id

        success = orchestrator.execute_task(task)

        # --- CONTROLLED FAILURE PROPAGATION ---
        if not success:
            step["error"] = task.get("error", "Unknown task failure")
            workflow_manager.fail_step(workflow, step["step"])
            event_bus.emit(STEP_FAILED, step)
            step_failed_flag = True
            break

        # --- SUCCESS PATH (should NOT be reached) ---
        workflow_manager.complete_step(workflow, step["step"])
        event_bus.emit(STEP_COMPLETED, step)

    except Exception as e:
        # Unexpected exception from capability or plumbing
        step["error"] = str(e)
        workflow_manager.fail_step(workflow, step["step"])
        event_bus.emit(STEP_FAILED, step)
        step_failed_flag = True
        break

if step_failed_flag:
    workflow_manager.fail_workflow(workflow)
    event_bus.emit(WORKFLOW_FAILED, workflow)

else:
    # All steps succeeded
    workflow_manager.complete_workflow(workflow)
    event_bus.emit(WORKFLOW_COMPLETED, workflow)



# ===========================================================================
# SECTION 5 — Restore patch (keeps environment clean)
# ===========================================================================

search_youtube_mod.execute = _original_execute
CAPABILITY_REGISTRY["search_youtube"] = _original_execute
print("\n[RESTORE] search_youtube.execute restored to original.")


# ===========================================================================
# SECTION 6 — Dump trace
# ===========================================================================

tracker.dump_trace()


# ===========================================================================
# SECTION 7 — Assertions (structured test results)
# ===========================================================================

PASS = "\033[92m  PASS\033[0m"
FAIL = "\033[91m  FAIL\033[0m"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    line = f"{status}  {label}"
    if detail:
        line += f"  [{detail}]"
    print(line)
    results.append((label, condition))

print("\n" + "=" * 60)
print("ASSERTION RESULTS")
print("=" * 60)

# ---- EVENT FIRING ----
check("TASK_FAILED emitted",
      tracker.was_emitted(TASK_FAILED),
      f"count={tracker.count(TASK_FAILED)}")

check("STEP_FAILED emitted",
      tracker.was_emitted(STEP_FAILED),
      f"count={tracker.count(STEP_FAILED)}")

check("WORKFLOW_FAILED emitted",
      tracker.was_emitted(WORKFLOW_FAILED),
      f"count={tracker.count(WORKFLOW_FAILED)}")

# ---- NO SUCCESS EVENTS ----
check("TASK_COMPLETED NOT emitted",
      not tracker.was_emitted(TASK_COMPLETED),
      f"count={tracker.count(TASK_COMPLETED)}")

check("WORKFLOW_COMPLETED NOT emitted",
      not tracker.was_emitted(WORKFLOW_COMPLETED),
      f"count={tracker.count(WORKFLOW_COMPLETED)}")

# ---- NO DUPLICATE EVENTS ----
check("TASK_FAILED emitted exactly once",
      tracker.count(TASK_FAILED) == 1,
      f"count={tracker.count(TASK_FAILED)}")

check("STEP_FAILED emitted exactly once",
      tracker.count(STEP_FAILED) == 1,
      f"count={tracker.count(STEP_FAILED)}")

check("WORKFLOW_FAILED emitted exactly once",
      tracker.count(WORKFLOW_FAILED) == 1,
      f"count={tracker.count(WORKFLOW_FAILED)}")

# ---- WORKFLOW STATE ----
check("workflow.state == FAILED",
      workflow["state"] == "FAILED",
      f"actual={workflow['state']}")

check("workflow removed from active_workflows",
      workflow_id not in workflow_manager.active_workflows,
      f"active_ids={list(workflow_manager.active_workflows.keys())}")

check("workflow added to failed_workflows",
      workflow_id in workflow_manager.failed_workflows,
      f"failed_ids={list(workflow_manager.failed_workflows.keys())}")

# ---- TASK STATE ----
# Find the task that was created (it's the only one)
task_failed_events = [(n, d) for n, d in tracker.log if n == TASK_FAILED]
task_data = task_failed_events[0][1] if task_failed_events else {}

check("task contains 'error' field",
      "error" in task_data and task_data["error"],
      f"error={task_data.get('error')}")

check("task.state == FAILED",
      task_data.get("state") == "FAILED",
      f"actual={task_data.get('state')}")

# ---- STEP STATE ----
failed_step = workflow["steps"][0]

check("step contains 'error' field",
      "error" in failed_step and failed_step["error"],
      f"error={failed_step.get('error')}")

check("step.state == FAILED",
      failed_step.get("state") == "FAILED",
      f"actual={failed_step.get('state')}")

# ---- WORKFLOW FAILURE INFO ----
check("workflow contains 'state' == FAILED",
      workflow.get("state") == "FAILED",
      f"actual={workflow.get('state')}")

# ---- RUNTIME STATE ----
# Task should NOT be in active_tasks (moved out on TASK_FAILED handler)
task_id = task_data.get("task_id", "")

check("task removed from runtime_state.active_tasks",
      task_id not in runtime_state.active_tasks,
      f"active_task_ids={list(runtime_state.active_tasks.keys())}")

check("task in runtime_state.failed_tasks",
      any(t.get("task_id") == task_id for t in runtime_state.failed_tasks),
      f"failed_count={len(runtime_state.failed_tasks)}")

check("task NOT in runtime_state.completed_tasks",
      not any(t.get("task_id") == task_id for t in runtime_state.completed_tasks),
      f"completed_count={len(runtime_state.completed_tasks)}")

# ---- STEP HALT: no further steps executed ----
check("only 1 step exists and it is FAILED (no continuation)",
      len(workflow["steps"]) == 1 and workflow["steps"][0]["state"] == "FAILED")

# ---- ERROR TEXT MATCHES INJECTION ----
check("task error matches injected message",
      INJECTED_ERROR in str(task_data.get("error", "")),
      f"error={task_data.get('error')}")

print("=" * 60)


# ===========================================================================
# SECTION 8 — Detailed runtime state dump
# ===========================================================================

print("\n[RUNTIME STATE DUMP]")
print(f"  active_tasks    : {runtime_state.active_tasks}")
print(f"  completed_tasks : {runtime_state.completed_tasks}")
print(f"  failed_tasks    : {[t.get('task_id') for t in runtime_state.failed_tasks]}")
print(f"\n[WORKFLOW MANAGER DUMP]")
print(f"  active_workflows   : {list(workflow_manager.active_workflows.keys())}")
print(f"  completed_workflows: {list(workflow_manager.completed_workflows.keys())}")
print(f"  failed_workflows   : {list(workflow_manager.failed_workflows.keys())}")
print(f"\n[FINAL WORKFLOW OBJECT]")
for k, v in workflow.items():
    if k != "steps":
        print(f"  {k}: {v}")
print("  steps:")
for s in workflow["steps"]:
    print(f"    {s}")


# ===========================================================================
# SECTION 9 — Verdict
# ===========================================================================

passed  = sum(1 for _, ok in results if ok)
failed  = sum(1 for _, ok in results if not ok)
total   = len(results)

print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} checks passed")

if failed == 0:
    print("\033[92m\nFINAL VERDICT: PASS\033[0m")
else:
    print(f"\033[91m\nFINAL VERDICT: FAIL  ({failed} check(s) failed)\033[0m")
    print("\nFailed checks:")
    for label, ok in results:
        if not ok:
            print(f"  x {label}")

print("=" * 60 + "\n")
