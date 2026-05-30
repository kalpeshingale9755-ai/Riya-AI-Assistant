"""
test_open_url.py
================
Tests for OPEN_URL intent support.

Sections:
  A. IntentDetector — OPEN_URL detection
     A1. http:// / https:// inline URLs
     A2. "go to <url>" prefix
     A3. "visit <url>" prefix
     A4. "open url <url>" prefix
     A5. Non-URL inputs must NOT produce OPEN_URL
     A6. Edge-cases: empty URL tail, no url entity when missing
  B. Planner — OPEN_URL plan generation
     B1. Valid URL produces 1-step plan with correct capability & payload
     B2. Missing / empty url entity produces []
  C. CLI integration — full runtime pipeline via core/main.py
     C1. "go to https://google.com" — success path (webbrowser mocked)
     C2. open_url capability failure propagates correctly (webbrowser raises)

Run:
    python test_open_url.py
"""

from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Bootstrap subscribers BEFORE any riya imports so singletons are clean.
# ---------------------------------------------------------------------------
import riya_engine.runtime.runtime_subscribers   # registers TASK_* handlers

from riya_engine.runtime.event_bus   import event_bus
from riya_engine.runtime.event_types import (
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED,   STEP_COMPLETED,   STEP_FAILED,
)
from riya_engine.workflows.workflow_manager import workflow_manager
from riya_engine.state.runtime_state        import runtime_state


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
# SECTION A — IntentDetector: OPEN_URL detection
# ===========================================================================

from riya_engine.intent.detector import intent_detector

print("\n" + "=" * 60)
print("A. IntentDetector — OPEN_URL detection")
print("=" * 60)

S = "IntentDetector OPEN_URL"


def detect(text):
    return intent_detector.detect(text)


# A1 — Inline http/https tokens
r = detect("https://google.com")
check(S, 'A1a: bare https URL -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "https://google.com",
      f"intent={r.intent} url={r.entities.get('url')}")

r = detect("http://example.com")
check(S, 'A1b: bare http URL -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "http://example.com",
      f"intent={r.intent} url={r.entities.get('url')}")

r = detect("open https://github.com")
check(S, 'A1c: "open https://..." -> OPEN_URL (not OPEN_APP)',
      r.intent == "OPEN_URL" and r.entities.get("url") == "https://github.com",
      f"intent={r.intent} url={r.entities.get('url')}")

r = detect("launch http://localhost:8080")
check(S, 'A1d: "launch http://..." -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "http://localhost:8080",
      f"intent={r.intent} url={r.entities.get('url')}")

# A2 — "go to" prefix
r = detect("go to https://youtube.com")
check(S, 'A2a: "go to https://..." -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "https://youtube.com",
      f"intent={r.intent} url={r.entities.get('url')}")

r = detect("go to www.google.com")
check(S, 'A2b: "go to www.google.com" -> OPEN_URL (bare domain)',
      r.intent == "OPEN_URL" and r.entities.get("url") == "www.google.com",
      f"intent={r.intent} url={r.entities.get('url')}")

# A3 — "visit" prefix
r = detect("visit https://openai.com")
check(S, 'A3a: "visit https://..." -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "https://openai.com",
      f"intent={r.intent} url={r.entities.get('url')}")

r = detect("visit github.com")
check(S, 'A3b: "visit github.com" -> OPEN_URL (bare domain)',
      r.intent == "OPEN_URL" and r.entities.get("url") == "github.com",
      f"intent={r.intent} url={r.entities.get('url')}")

# A4 — "open url" prefix
r = detect("open url https://docs.python.org")
check(S, 'A4a: "open url https://..." -> OPEN_URL',
      r.intent == "OPEN_URL" and r.entities.get("url") == "https://docs.python.org",
      f"intent={r.intent} url={r.entities.get('url')}")

# A5 — Non-URL inputs must NOT produce OPEN_URL
r = detect("open chrome")
check(S, 'A5a: "open chrome" -> OPEN_APP (not OPEN_URL)',
      r.intent == "OPEN_APP",
      f"intent={r.intent}")

r = detect("open notepad")
check(S, 'A5b: "open notepad" -> OPEN_APP (not OPEN_URL)',
      r.intent == "OPEN_APP",
      f"intent={r.intent}")

r = detect("search youtube lofi music")
check(S, 'A5c: "search youtube ..." -> SEARCH_YOUTUBE (not OPEN_URL)',
      r.intent == "SEARCH_YOUTUBE",
      f"intent={r.intent}")

r = detect("close chrome")
check(S, 'A5d: "close chrome" -> CLOSE_APP (not OPEN_URL)',
      r.intent == "CLOSE_APP",
      f"intent={r.intent}")

# A6 — Edge-cases
r = detect("go to ")
check(S, 'A6a: "go to " (empty tail) -> UNKNOWN',
      r.intent == "UNKNOWN",
      f"intent={r.intent}")

r = detect("visit")
check(S, 'A6b: "visit" alone -> UNKNOWN (no tail)',
      r.intent == "UNKNOWN",
      f"intent={r.intent}")

r = detect("")
check(S, 'A6c: empty string -> UNKNOWN',
      r.intent == "UNKNOWN",
      f"intent={r.intent}")


# ===========================================================================
# SECTION B — Planner: OPEN_URL plan generation
# ===========================================================================

from riya_engine.planner.planner      import planner
from riya_engine.intent.intent_response import IntentResponse

print("\n" + "=" * 60)
print("B. Planner — OPEN_URL plan generation")
print("=" * 60)

S = "Planner OPEN_URL"


def make_resp(intent, entities=None):
    return IntentResponse(intent=intent, confidence=0.95, entities=entities or {})


# B1 — Valid URL
plan = planner.create_plan(make_resp("OPEN_URL", {"url": "https://google.com"}))
check(S, 'B1a: OPEN_URL valid -> 1-step plan',
      len(plan) == 1,
      f"len={len(plan)}")
check(S, 'B1b: capability == "open_url"',
      len(plan) == 1 and plan[0].get("capability") == "open_url",
      f"capability={plan[0].get('capability') if plan else 'N/A'}")
check(S, 'B1c: payload.url == "https://google.com"',
      len(plan) == 1 and plan[0].get("payload", {}).get("url") == "https://google.com",
      f"payload={plan[0].get('payload') if plan else 'N/A'}")
check(S, 'B1d: step == 1',
      len(plan) == 1 and plan[0].get("step") == 1,
      f"step={plan[0].get('step') if plan else 'N/A'}")

# B2 — Missing / empty url → guard returns []
plan = planner.create_plan(make_resp("OPEN_URL"))
check(S, 'B2a: OPEN_URL no url entity -> []',
      plan == [],
      f"plan={plan}")

plan = planner.create_plan(make_resp("OPEN_URL", {"url": ""}))
check(S, 'B2b: OPEN_URL empty-string url -> []',
      plan == [],
      f"plan={plan}")

plan = planner.create_plan(make_resp("OPEN_URL", {"url": None}))
check(S, 'B2c: OPEN_URL None url -> []',
      plan == [],
      f"plan={plan}")

# B3 — Existing intents still work after the addition
plan = planner.create_plan(make_resp("OPEN_APP", {"app_name": "chrome"}))
check(S, 'B3a: OPEN_APP still produces 1-step plan',
      len(plan) == 1 and plan[0]["capability"] == "open_app")

plan = planner.create_plan(make_resp("CLOSE_APP", {"app_name": "notepad"}))
check(S, 'B3b: CLOSE_APP still produces 1-step plan',
      len(plan) == 1 and plan[0]["capability"] == "close_app")

plan = planner.create_plan(make_resp("SEARCH_YOUTUBE", {"query": "lofi"}))
check(S, 'B3c: SEARCH_YOUTUBE still produces 2-step plan',
      len(plan) == 2)


# ===========================================================================
# SECTION C — CLI integration: full runtime pipeline
# ===========================================================================

from core.main import run

print("\n" + "=" * 60)
print("C. CLI integration — OPEN_URL end-to-end")
print("=" * 60)


_ALL_EVENTS = [
    WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED,
    STEP_STARTED, STEP_COMPLETED, STEP_FAILED,
    TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED,
]


class _Tracker:
    def __init__(self, label):
        self.label = label
        self.log   = []
        self._cnt  = {}
        self._hs   = []

    def attach(self, events):
        for evt in events:
            def _h(data, _e=evt):
                snap = dict(data) if isinstance(data, dict) else data
                self.log.append((_e, snap))
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


def _reset():
    workflow_manager.active_workflows.clear()
    workflow_manager.completed_workflows.clear()
    workflow_manager.failed_workflows.clear()
    runtime_state.active_tasks.clear()
    runtime_state.completed_tasks.clear()
    runtime_state.failed_tasks.clear()


def run_scenario(label, inputs, *, wb_open_side_effect=None):
    """
    Feed inputs into run(), optionally controlling webbrowser.open's behaviour.
    Returns a _Tracker.
    """
    _reset()
    t = _Tracker(label)
    t.attach(_ALL_EVENTS)

    seq = iter(inputs + ["exit"])

    wb_kwargs = (
        {"side_effect": wb_open_side_effect}
        if wb_open_side_effect is not None
        else {"return_value": True}
    )

    with patch("builtins.input",   side_effect=lambda _="": next(seq)), \
         patch("subprocess.Popen", return_value=MagicMock()), \
         patch("subprocess.run",   return_value=MagicMock(returncode=0)), \
         patch("webbrowser.open",  **wb_kwargs):
        try:
            run()
        except StopIteration:
            pass

    t.detach()
    return t


# --- C1: success path ---
print("\n  [Scenario] go to https://google.com")
t = run_scenario("go to https://google.com", ["go to https://google.com"])

S = "C1 open_url success"
check(S, "WORKFLOW_STARTED emitted",    t.ok(WORKFLOW_STARTED))
check(S, "STEP_STARTED emitted",        t.ok(STEP_STARTED))
check(S, "TASK_CREATED emitted",        t.ok(TASK_CREATED))
check(S, "TASK_COMPLETED emitted",      t.ok(TASK_COMPLETED),
      f"count={t.count(TASK_COMPLETED)}")
check(S, "STEP_COMPLETED emitted",      t.ok(STEP_COMPLETED))
check(S, "WORKFLOW_COMPLETED emitted",  t.ok(WORKFLOW_COMPLETED))
check(S, "TASK_FAILED NOT emitted",     not t.ok(TASK_FAILED),
      f"count={t.count(TASK_FAILED)}")
check(S, "WORKFLOW_FAILED NOT emitted", not t.ok(WORKFLOW_FAILED),
      f"count={t.count(WORKFLOW_FAILED)}")
check(S, "1 completed workflow",
      len(workflow_manager.completed_workflows) == 1,
      f"count={len(workflow_manager.completed_workflows)}")
check(S, "active_workflows empty",
      len(workflow_manager.active_workflows) == 0)
check(S, "1 completed task in runtime_state",
      len(runtime_state.completed_tasks) == 1,
      f"count={len(runtime_state.completed_tasks)}")

# --- C2: open https:// inline token ---
print("\n  [Scenario] open https://github.com")
t = run_scenario("open https://github.com", ["open https://github.com"])

S = "C2 open_url inline token"
check(S, "WORKFLOW_COMPLETED emitted",  t.ok(WORKFLOW_COMPLETED))
check(S, "TASK_COMPLETED emitted",      t.ok(TASK_COMPLETED))
check(S, "TASK_FAILED NOT emitted",     not t.ok(TASK_FAILED))
check(S, "WORKFLOW_FAILED NOT emitted", not t.ok(WORKFLOW_FAILED))

# --- C3: webbrowser raises — failure propagates ---
print("\n  [Scenario] failure — webbrowser.open raises")
t = run_scenario(
    "open_url failure",
    ["go to https://bad.url"],
    wb_open_side_effect=Exception("connection refused"),
)

S = "C3 open_url failure propagation"
check(S, "TASK_FAILED emitted",          t.ok(TASK_FAILED),
      f"count={t.count(TASK_FAILED)}")
check(S, "STEP_FAILED emitted",          t.ok(STEP_FAILED))
check(S, "WORKFLOW_FAILED emitted",      t.ok(WORKFLOW_FAILED))
check(S, "TASK_COMPLETED NOT emitted",   not t.ok(TASK_COMPLETED))
check(S, "WORKFLOW_COMPLETED NOT emitted", not t.ok(WORKFLOW_COMPLETED))
check(S, "1 failed workflow",
      len(workflow_manager.failed_workflows) == 1,
      f"count={len(workflow_manager.failed_workflows)}")
check(S, "1 failed task in runtime_state",
      len(runtime_state.failed_tasks) == 1,
      f"count={len(runtime_state.failed_tasks)}")


# ===========================================================================
# Summary
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
    total_p += p
    total_f += f
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
