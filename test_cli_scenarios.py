"""
test_cli_scenarios.py
=====================
Full CLI simulation test for Riya v2.

Scenarios:
  1. open chrome
  2. open chrome and close it
  3. search youtube lofi music
  4. intentional failure test (capability raises exception)

Strategy:
  - Patches builtins.input to feed canned inputs to run()
  - Patches subprocess.Popen and webbrowser.open to avoid real side-effects
  - Injects a failing capability for scenario 4 via monkey-patch
  - Tracks every event emission with lightweight listeners
  - Asserts invariants per scenario after the run
  - Restores all patches at the end

Run:
    python test_cli_scenarios.py
"""

import builtins
import subprocess
import webbrowser
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Bootstrap — must happen BEFORE any riya imports to ensure singleton state
# is clean on first load.
# ---------------------------------------------------------------------------
import riya_engine.runtime.runtime_subscribers   # TASK_* handlers
# debug_subscriber skipped — too noisy in batch mode

from riya_engine.runtime.event_bus    import event_bus
from riya_engine.runtime.event_types  import (
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED,   STEP_COMPLETED,   STEP_FAILED,
)
from riya_engine.capabilities.registry import CAPABILITY_REGISTRY
import riya_engine.capabilities.open_app       as open_app_mod
import riya_engine.capabilities.search_youtube as search_youtube_mod
from riya_engine.workflows.workflow_manager     import workflow_manager
from riya_engine.state.runtime_state            import runtime_state
from riya_engine.memory.memory_orchestrator     import memory


# ===========================================================================
# SECTION 1 — Utilities
# ===========================================================================

PASS_COLOR = "\033[92mPASS\033[0m"
FAIL_COLOR = "\033[91mFAIL\033[0m"


class ScenarioTracker:
    """Per-scenario event recorder."""

    def __init__(self, label):
        self.label   = label
        self.log     = []     # (event_name, snapshot_of_data)
        self._counts = {}
        self._handles = []

    def attach(self, events):
        for evt in events:
            def _h(data, _evt=evt):
                # Shallow-copy dict so mutations after emission don't corrupt log
                snap = dict(data) if isinstance(data, dict) else data
                self.log.append((_evt, snap))
                self._counts[_evt] = self._counts.get(_evt, 0) + 1
            _h.__name__ = f"tracker_{evt}"
            event_bus.subscribe(evt, _h)
            self._handles.append((evt, _h))

    def detach(self):
        for evt, h in self._handles:
            event_bus.unsubscribe(evt, h)
        self._handles.clear()

    def count(self, evt):
        return self._counts.get(evt, 0)

    def emitted(self, evt):
        return self._counts.get(evt, 0) > 0

    def trace(self):
        lines = [f"\n  --- Trace: {self.label} ---"]
        for i, (name, data) in enumerate(self.log, 1):
            extra = ""
            if isinstance(data, dict):
                bits = []
                for k in ("state", "error", "capability", "intent", "step"):
                    if k in data:
                        bits.append(f"{k}={data[k]}")
                extra = "  " + ", ".join(bits)
            lines.append(f"  [{i:02d}] {name}{extra}")
        return "\n".join(lines)


ALL_EVENTS = [
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED,   STEP_COMPLETED,   STEP_FAILED,
]

results = []   # global list of (scenario_label, check_label, pass)

def check(scenario, label, condition, detail=""):
    ok = bool(condition)
    tag = PASS_COLOR if ok else FAIL_COLOR
    msg = f"  [{tag}] {label}"
    if detail:
        msg += f"  [{detail}]"
    print(msg)
    results.append((scenario, label, ok))
    return ok


# ===========================================================================
# SECTION 2 — Reset helpers
# ===========================================================================

def reset_workflow_manager():
    """Clear all workflow manager state between scenarios."""
    workflow_manager.active_workflows.clear()
    workflow_manager.completed_workflows.clear()
    workflow_manager.failed_workflows.clear()


def reset_runtime_state():
    """Clear runtime_state between scenarios."""
    runtime_state.active_tasks.clear()
    runtime_state.completed_tasks.clear()
    runtime_state.failed_tasks.clear()


def full_reset():
    reset_workflow_manager()
    reset_runtime_state()


# ===========================================================================
# SECTION 3 — Import the run() function (with input() monkey-patchable)
# ===========================================================================

from core.main import run


# ===========================================================================
# SECTION 4 — Run a scenario
# ===========================================================================

def run_scenario(label, inputs):
    """
    Feed `inputs` into run() one by one, then append 'exit' to stop the loop.
    Returns a ScenarioTracker loaded with all events emitted during this run.
    """
    full_reset()
    tracker = ScenarioTracker(label)
    tracker.attach(ALL_EVENTS)

    input_seq = inputs + ["exit"]
    call_iter  = iter(input_seq)

    with patch("builtins.input", side_effect=lambda _="You: ": next(call_iter)), \
         patch("subprocess.Popen",      return_value=MagicMock()), \
         patch("subprocess.run",        return_value=MagicMock(returncode=0)), \
         patch("webbrowser.open",       return_value=True):
        try:
            run()
        except StopIteration:
            pass   # exhausted inputs safely

    tracker.detach()
    print(tracker.trace())
    return tracker


# ===========================================================================
# SCENARIO 1 — "open chrome"
# ===========================================================================

print("\n" + "=" * 60)
print("SCENARIO 1: open chrome")
print("=" * 60)

t1 = run_scenario("open chrome", ["open chrome"])

S = "open chrome"
check(S, "WORKFLOW_STARTED emitted",        t1.emitted(WORKFLOW_STARTED))
check(S, "STEP_STARTED emitted",            t1.emitted(STEP_STARTED))
check(S, "TASK_CREATED emitted",            t1.emitted(TASK_CREATED))
check(S, "TASK_STARTED emitted",            t1.emitted(TASK_STARTED))
check(S, "TASK_COMPLETED emitted",          t1.emitted(TASK_COMPLETED), f"count={t1.count(TASK_COMPLETED)}")
check(S, "STEP_COMPLETED emitted",          t1.emitted(STEP_COMPLETED))
check(S, "WORKFLOW_COMPLETED emitted",      t1.emitted(WORKFLOW_COMPLETED))
check(S, "TASK_FAILED NOT emitted",         not t1.emitted(TASK_FAILED),     f"count={t1.count(TASK_FAILED)}")
check(S, "WORKFLOW_FAILED NOT emitted",     not t1.emitted(WORKFLOW_FAILED), f"count={t1.count(WORKFLOW_FAILED)}")
check(S, "workflow in completed_workflows", len(workflow_manager.completed_workflows) == 1)
check(S, "active_workflows empty",          len(workflow_manager.active_workflows) == 0)
check(S, "completed_tasks has 1 entry",     len(runtime_state.completed_tasks) == 1)
# OPEN_OPEN_APP check — action stored in context_memory must be OPEN_APP not OPEN_OPEN_APP
stored_action = memory.get_last_action()
check(S, "stored action == OPEN_APP (not OPEN_OPEN_APP)",
      stored_action == "OPEN_APP",
      f"actual='{stored_action}'")


# ===========================================================================
# SCENARIO 2 — "open chrome and close it"
# ===========================================================================

print("\n" + "=" * 60)
print("SCENARIO 2: open chrome and close it")
print("=" * 60)

t2 = run_scenario("open chrome and close it", ["open chrome and close it"])

S = "open chrome and close it"
check(S, "WORKFLOW_STARTED emitted (>=1)",  t2.count(WORKFLOW_STARTED) >= 1,
      f"count={t2.count(WORKFLOW_STARTED)}")
check(S, "TASK_COMPLETED emitted",          t2.emitted(TASK_COMPLETED))
check(S, "STEP_COMPLETED emitted",          t2.emitted(STEP_COMPLETED))
check(S, "WORKFLOW_COMPLETED emitted",      t2.emitted(WORKFLOW_COMPLETED))
check(S, "TASK_FAILED NOT emitted",         not t2.emitted(TASK_FAILED))
check(S, "WORKFLOW_FAILED NOT emitted",     not t2.emitted(WORKFLOW_FAILED))
check(S, "active_workflows empty",          len(workflow_manager.active_workflows) == 0)
check(S, "all completed_workflows",
      len(workflow_manager.failed_workflows) == 0,
      f"failed={len(workflow_manager.failed_workflows)}")


# ===========================================================================
# SCENARIO 3 — "search youtube lofi music"
# ===========================================================================

print("\n" + "=" * 60)
print("SCENARIO 3: search youtube lofi music")
print("=" * 60)

t3 = run_scenario("search youtube lofi music", ["search youtube lofi music"])

S = "search youtube lofi music"
check(S, "WORKFLOW_STARTED emitted",    t3.emitted(WORKFLOW_STARTED))
check(S, "STEP_STARTED emitted (>=2)",  t3.count(STEP_STARTED) >= 2,
      f"count={t3.count(STEP_STARTED)}")
check(S, "TASK_COMPLETED emitted (>=2)",t3.count(TASK_COMPLETED) >= 2,
      f"count={t3.count(TASK_COMPLETED)}")
check(S, "STEP_COMPLETED emitted (>=2)",t3.count(STEP_COMPLETED) >= 2,
      f"count={t3.count(STEP_COMPLETED)}")
check(S, "WORKFLOW_COMPLETED emitted",  t3.emitted(WORKFLOW_COMPLETED))
check(S, "TASK_FAILED NOT emitted",     not t3.emitted(TASK_FAILED))
check(S, "WORKFLOW_FAILED NOT emitted", not t3.emitted(WORKFLOW_FAILED))
check(S, "active_workflows empty",      len(workflow_manager.active_workflows) == 0)
check(S, "1 workflow completed",
      len(workflow_manager.completed_workflows) == 1,
      f"count={len(workflow_manager.completed_workflows)}")


# ===========================================================================
# SCENARIO 4 — Intentional failure test
# (patch open_app.execute to raise for this scenario only)
# ===========================================================================

print("\n" + "=" * 60)
print("SCENARIO 4: intentional failure test")
print("=" * 60)

INJECTED_ERROR = "Intentional workflow failure test"
_orig_open_app = open_app_mod.execute

def _failing_open_app(payload):
    raise Exception(INJECTED_ERROR)

open_app_mod.execute = _failing_open_app
CAPABILITY_REGISTRY["open_app"] = _failing_open_app

t4 = run_scenario("intentional failure", ["open chrome"])

# Restore
open_app_mod.execute = _orig_open_app
CAPABILITY_REGISTRY["open_app"] = _orig_open_app

S = "intentional failure"
check(S, "TASK_FAILED emitted",             t4.emitted(TASK_FAILED),
      f"count={t4.count(TASK_FAILED)}")
check(S, "STEP_FAILED emitted",             t4.emitted(STEP_FAILED),
      f"count={t4.count(STEP_FAILED)}")
check(S, "WORKFLOW_FAILED emitted",         t4.emitted(WORKFLOW_FAILED),
      f"count={t4.count(WORKFLOW_FAILED)}")
check(S, "TASK_FAILED exactly once",        t4.count(TASK_FAILED) == 1,
      f"count={t4.count(TASK_FAILED)}")
check(S, "STEP_FAILED exactly once",        t4.count(STEP_FAILED) == 1,
      f"count={t4.count(STEP_FAILED)}")
check(S, "WORKFLOW_FAILED exactly once",    t4.count(WORKFLOW_FAILED) == 1,
      f"count={t4.count(WORKFLOW_FAILED)}")
check(S, "TASK_COMPLETED NOT emitted",      not t4.emitted(TASK_COMPLETED))
check(S, "WORKFLOW_COMPLETED NOT emitted",  not t4.emitted(WORKFLOW_COMPLETED))
check(S, "workflow in failed_workflows",
      len(workflow_manager.failed_workflows) == 1,
      f"count={len(workflow_manager.failed_workflows)}")
check(S, "active_workflows empty",
      len(workflow_manager.active_workflows) == 0)
check(S, "task in runtime_state.failed_tasks",
      len(runtime_state.failed_tasks) == 1)
check(S, "task error matches injected message",
      any(INJECTED_ERROR in str(t.get("error",""))
          for t in runtime_state.failed_tasks))

# Retrieve the failed task from the trace to check its fields
failed_task_events = [(n, d) for n, d in t4.log if n == TASK_FAILED]
ftask = failed_task_events[0][1] if failed_task_events else {}
check(S, "task.state == FAILED",
      ftask.get("state") == "FAILED",
      f"actual={ftask.get('state')}")
check(S, "task contains error field",
      bool(ftask.get("error")),
      f"error={ftask.get('error')}")

# Check step
wf_list = list(workflow_manager.failed_workflows.values())
if wf_list:
    failed_step = wf_list[0]["steps"][0]
    check(S, "step.state == FAILED",
          failed_step.get("state") == "FAILED",
          f"actual={failed_step.get('state')}")
    check(S, "step contains error field",
          bool(failed_step.get("error")),
          f"error={failed_step.get('error')}")
else:
    check(S, "step.state == FAILED",       False, "no failed workflow found")
    check(S, "step contains error field",  False, "no failed workflow found")


# ===========================================================================
# SECTION 5 — Summary
# ===========================================================================

print("\n" + "=" * 60)
print("FULL SUMMARY")
print("=" * 60)

by_scenario = {}
for sc, label, ok in results:
    by_scenario.setdefault(sc, []).append((label, ok))

total_pass = total_fail = 0

for sc, checks in by_scenario.items():
    sc_pass = sum(1 for _, ok in checks if ok)
    sc_fail = sum(1 for _, ok in checks if not ok)
    total_pass += sc_pass
    total_fail += sc_fail
    status = PASS_COLOR if sc_fail == 0 else FAIL_COLOR
    print(f"\n  [{status}] {sc}  ({sc_pass}/{len(checks)})")
    for label, ok in checks:
        tag = PASS_COLOR if ok else FAIL_COLOR
        print(f"           [{tag}] {label}")

print("\n" + "=" * 60)
print(f"TOTALS: {total_pass}/{total_pass + total_fail} checks passed")
if total_fail == 0:
    print("\033[92m\nFINAL VERDICT: PASS\033[0m")
else:
    print(f"\033[91m\nFINAL VERDICT: FAIL  ({total_fail} check(s) failed)\033[0m")
    print("\nFailed:")
    for sc, label, ok in results:
        if not ok:
            print(f"  x [{sc}] {label}")
print("=" * 60 + "\n")
