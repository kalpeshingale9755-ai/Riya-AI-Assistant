"""
test_planner_layer.py
=====================
Tests for the planner layer improvements.

Sections:
  A. normalize_app_name unit tests
  B. IntentDetector unit tests  (open/close — notepad, vscode, chrome, aliases)
  C. Planner validation tests   (PV-01, PV-02, PV-03 guards)
  D. CLI simulation             (open notepad, close notepad, open vscode, close vscode)

Nothing in the workflow / orchestrator / event-bus / task-manager /
memory layers is modified. subprocess and webbrowser are mocked throughout.

Run:
    python test_planner_layer.py
"""

import builtins
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Shared colour helpers
# ---------------------------------------------------------------------------

_G = "\033[92mPASS\033[0m"
_R = "\033[91mFAIL\033[0m"

results = []   # (section, label, ok)

def check(section, label, condition, detail=""):
    ok  = bool(condition)
    msg = f"  [{_G if ok else _R}] {label}"
    if detail:
        msg += f"  [{detail}]"
    print(msg)
    results.append((section, label, ok))
    return ok


# ===========================================================================
# SECTION A — normalize_app_name
# ===========================================================================

from riya_engine.nlp.entity_normalizer import normalize_app_name

print("\n" + "=" * 60)
print("A. normalize_app_name")
print("=" * 60)

S = "normalize_app_name"
check(S, '"chrome" -> chrome',               normalize_app_name("chrome")              == "chrome")
check(S, '"google chrome" -> chrome',        normalize_app_name("google chrome")       == "chrome")
check(S, '"browser" -> chrome',              normalize_app_name("browser")             == "chrome")
check(S, '"notepad" -> notepad',             normalize_app_name("notepad")             == "notepad")
check(S, '"text editor" -> notepad',         normalize_app_name("text editor")         == "notepad")
check(S, '"vscode" -> vscode',               normalize_app_name("vscode")              == "vscode")
check(S, '"visual studio code" -> vscode',   normalize_app_name("visual studio code")  == "vscode")
check(S, '"vs code" -> vscode',              normalize_app_name("vs code")             == "vscode")
check(S, '"code" -> vscode',                 normalize_app_name("code")                == "vscode")
check(S, 'unknown app passes through',       normalize_app_name("spotify")             == "spotify")
check(S, 'empty string returns None',        normalize_app_name("")                    is None)
check(S, 'None returns None',                normalize_app_name(None)                  is None)


# ===========================================================================
# SECTION B — IntentDetector
# ===========================================================================

# Bootstrap subscribers before importing detector (event_bus singleton)
import riya_engine.runtime.runtime_subscribers

from riya_engine.intent.detector import intent_detector

print("\n" + "=" * 60)
print("B. IntentDetector — general app resolution")
print("=" * 60)

S = "IntentDetector"

def detect(text):
    return intent_detector.detect(text)

# ---- OPEN APP ----
r = detect("open chrome")
check(S, '"open chrome" -> OPEN_APP chrome',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "chrome",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("open notepad")
check(S, '"open notepad" -> OPEN_APP notepad',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "notepad",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("open vscode")
check(S, '"open vscode" -> OPEN_APP vscode',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "vscode",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("open visual studio code")
check(S, '"open visual studio code" -> OPEN_APP vscode',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "vscode",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("launch notepad")
check(S, '"launch notepad" -> OPEN_APP notepad',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "notepad",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("start vscode")
check(S, '"start vscode" -> OPEN_APP vscode',
      r.intent == "OPEN_APP" and r.entities.get("app_name") == "vscode",
      f"intent={r.intent} app={r.entities.get('app_name')}")

# ---- CLOSE APP ----
r = detect("close chrome")
check(S, '"close chrome" -> CLOSE_APP chrome',
      r.intent == "CLOSE_APP" and r.entities.get("app_name") == "chrome",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("close notepad")
check(S, '"close notepad" -> CLOSE_APP notepad',
      r.intent == "CLOSE_APP" and r.entities.get("app_name") == "notepad",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("close vscode")
check(S, '"close vscode" -> CLOSE_APP vscode',
      r.intent == "CLOSE_APP" and r.entities.get("app_name") == "vscode",
      f"intent={r.intent} app={r.entities.get('app_name')}")

r = detect("quit notepad")
check(S, '"quit notepad" -> CLOSE_APP notepad',
      r.intent == "CLOSE_APP" and r.entities.get("app_name") == "notepad",
      f"intent={r.intent} app={r.entities.get('app_name')}")

# ---- SEARCH YOUTUBE ----
r = detect("search youtube lofi music")
check(S, '"search youtube lofi music" -> SEARCH_YOUTUBE',
      r.intent == "SEARCH_YOUTUBE" and r.entities.get("query") == "lofi music",
      f"intent={r.intent} query={r.entities.get('query')}")

# ---- UNKNOWN ----
r = detect("an intentional failure test")
check(S, 'unrecognised input -> UNKNOWN',
      r.intent == "UNKNOWN",
      f"intent={r.intent}")

r = detect("open")    # keyword with no app phrase
check(S, '"open" alone -> UNKNOWN (no app name)',
      r.intent == "UNKNOWN",
      f"intent={r.intent}")


# ===========================================================================
# SECTION C — Planner validation guards
# ===========================================================================

from riya_engine.planner.planner      import planner
from riya_engine.intent.intent_response import IntentResponse

print("\n" + "=" * 60)
print("C. Planner validation guards")
print("=" * 60)

S = "Planner validation"

def make_resp(intent, entities=None):
    return IntentResponse(intent=intent, confidence=0.9, entities=entities or {})

# PV-01 — OPEN_APP missing app_name
plan = planner.create_plan(make_resp("OPEN_APP"))
check(S, "PV-01: OPEN_APP no app_name -> []",
      plan == [], f"plan={plan}")

# PV-01 -- OPEN_APP valid
plan = planner.create_plan(make_resp("OPEN_APP", {"app_name": "notepad"}))
check(S, "PV-01: OPEN_APP notepad -> 1-step plan",
      len(plan) == 1 and plan[0]["payload"]["app_name"] == "notepad")

# PV-02 -- CLOSE_APP missing app_name
plan = planner.create_plan(make_resp("CLOSE_APP"))
check(S, "PV-02: CLOSE_APP no app_name -> []",
      plan == [], f"plan={plan}")

# PV-02 -- CLOSE_APP valid
plan = planner.create_plan(make_resp("CLOSE_APP", {"app_name": "vscode"}))
check(S, "PV-02: CLOSE_APP vscode -> 1-step plan",
      len(plan) == 1 and plan[0]["payload"]["app_name"] == "vscode")

# PV-03 -- SEARCH_YOUTUBE empty query
plan = planner.create_plan(make_resp("SEARCH_YOUTUBE", {"query": ""}))
check(S, "PV-03: SEARCH_YOUTUBE empty query -> []",
      plan == [], f"plan={plan}")

plan = planner.create_plan(make_resp("SEARCH_YOUTUBE", {"query": None}))
check(S, "PV-03: SEARCH_YOUTUBE None query -> []",
      plan == [], f"plan={plan}")

# PV-03 -- SEARCH_YOUTUBE valid
plan = planner.create_plan(make_resp("SEARCH_YOUTUBE", {"query": "lofi"}))
check(S, "PV-03: SEARCH_YOUTUBE valid query -> 2-step plan",
      len(plan) == 2)


# ===========================================================================
# SECTION D — CLI simulation (open/close notepad and vscode)
# ===========================================================================

import riya_engine.runtime.debug_subscriber   # optional trace

from riya_engine.runtime.event_bus   import event_bus
from riya_engine.runtime.event_types import (
    TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED, STEP_COMPLETED, STEP_FAILED,
    WORKFLOW_STARTED,
)
from riya_engine.workflows.workflow_manager import workflow_manager
from riya_engine.state.runtime_state        import runtime_state
from core.main import run


class _Tracker:
    def __init__(self, label):
        self.label = label
        self.log   = []
        self._cnt  = {}
        self._hs   = []

    def attach(self, events):
        for evt in events:
            def _h(data, _e=evt):
                self.log.append((_e, data))
                self._cnt[_e] = self._cnt.get(_e, 0) + 1
            _h.__name__ = f"t_{evt}"
            event_bus.subscribe(evt, _h)
            self._hs.append((evt, _h))

    def detach(self):
        for evt, h in self._hs:
            event_bus.unsubscribe(evt, h)
        self._hs.clear()

    def count(self, e): return self._cnt.get(e, 0)
    def ok(self,   e): return self._cnt.get(e, 0) > 0


_ALL = [
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED, STEP_COMPLETED, STEP_FAILED,
    TASK_COMPLETED, TASK_FAILED,
]


def run_scenario(label, inputs):
    workflow_manager.active_workflows.clear()
    workflow_manager.completed_workflows.clear()
    workflow_manager.failed_workflows.clear()
    runtime_state.active_tasks.clear()
    runtime_state.completed_tasks.clear()
    runtime_state.failed_tasks.clear()

    t = _Tracker(label)
    t.attach(_ALL)

    seq = iter(inputs + ["exit"])
    with patch("builtins.input",    side_effect=lambda _="": next(seq)), \
         patch("subprocess.Popen",  return_value=MagicMock()), \
         patch("subprocess.run",    return_value=MagicMock(returncode=0)), \
         patch("webbrowser.open",   return_value=True):
        try:
            run()
        except StopIteration:
            pass

    t.detach()
    return t


print("\n" + "=" * 60)
print("D. CLI simulation — notepad and vscode")
print("=" * 60)

for app in ("notepad", "vscode"):

    # --- open ---
    label = f"open {app}"
    print(f"\n  [Scenario] {label}")
    t = run_scenario(label, [f"open {app}"])
    S = label
    check(S, "WORKFLOW_COMPLETED emitted",    t.ok(WORKFLOW_COMPLETED))
    check(S, "TASK_COMPLETED emitted",        t.ok(TASK_COMPLETED))
    check(S, "WORKFLOW_FAILED NOT emitted",   not t.ok(WORKFLOW_FAILED))
    check(S, "TASK_FAILED NOT emitted",       not t.ok(TASK_FAILED))
    check(S, "active_workflows empty",
          len(workflow_manager.active_workflows) == 0)
    check(S, "completed_workflows has 1",
          len(workflow_manager.completed_workflows) == 1)

    # --- close ---
    label = f"close {app}"
    print(f"\n  [Scenario] {label}")
    t = run_scenario(label, [f"close {app}"])
    S = label
    check(S, "WORKFLOW_COMPLETED emitted",    t.ok(WORKFLOW_COMPLETED))
    check(S, "TASK_COMPLETED emitted",        t.ok(TASK_COMPLETED))
    check(S, "WORKFLOW_FAILED NOT emitted",   not t.ok(WORKFLOW_FAILED))
    check(S, "TASK_FAILED NOT emitted",       not t.ok(TASK_FAILED))
    check(S, "active_workflows empty",
          len(workflow_manager.active_workflows) == 0)
    check(S, "completed_workflows has 1",
          len(workflow_manager.completed_workflows) == 1)


# ===========================================================================
# Final summary
# ===========================================================================

by_sec = {}
for sc, lb, ok in results:
    by_sec.setdefault(sc, []).append((lb, ok))

total_p = total_f = 0

print("\n" + "=" * 60)
print("FULL SUMMARY")
print("=" * 60)

for sc, checks in by_sec.items():
    p = sum(1 for _, ok in checks if ok)
    f = sum(1 for _, ok in checks if not ok)
    total_p += p; total_f += f
    tag = _G if f == 0 else _R
    print(f"\n  [{tag}] {sc}  ({p}/{len(checks)})")
    for lb, ok in checks:
        print(f"           [{_G if ok else _R}] {lb}")

print("\n" + "=" * 60)
print(f"TOTALS: {total_p}/{total_p + total_f} checks passed")
if total_f == 0:
    print("\033[92m\nFINAL VERDICT: PASS\033[0m")
else:
    print(f"\033[91m\nFINAL VERDICT: FAIL  ({total_f} failed)\033[0m")
    for sc, lb, ok in results:
        if not ok:
            print(f"  x [{sc}] {lb}")
print("=" * 60 + "\n")
