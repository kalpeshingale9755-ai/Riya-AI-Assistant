# Riya V2 — Architecture Migration Report
**Date:** 2026-05-27  
**Status:** Active Development  
**Goal:** Stabilize Riya V2 into a scalable orchestrated AI runtime architecture before Riya V3 autonomous-agent systems.

---

## 1. Current Runtime Architecture Overview

Riya V2 is in a **transitional state** — it was built with an older linear pipeline (`engine.py` + `execution/executor.py`) and is being actively migrated to a new **runtime-centered architecture** centered around the `riya_engine/runtime/` module.

There are currently **two separate execution pipelines** coexisting in the same codebase, which is the primary architectural problem.

### Two Parallel Entry Points

| Entry Point | Pipeline Used | Status |
|---|---|---|
| `core/main.py` | New Runtime (Orchestrator → TaskManager → EventBus) | ✅ Active / New |
| `riya_engine/engine.py` | Old Linear (engine.process → executor.execute) | ⚠️ Deprecated (partially active) |

---

## 2. Active Subsystems

### 2.1 Runtime Module (`riya_engine/runtime/`)

The new runtime is the **intended authority** for all execution. It contains:

| File | Role | Status |
|---|---|---|
| `orchestrator.py` | Resolves capability from registry, executes task | ✅ Stable |
| `task_manager.py` | Creates, starts, completes, and fails tasks with UUIDs | ✅ Stable |
| `event_bus.py` | Publish/subscribe event dispatcher (singleton) | ✅ Stable |
| `events.py` | Enum-style event name constants | ✅ Stable |
| `execution_context.py` | Per-request context object (request_id, session_id, intent, plan, tasks) | ✅ Stable (underused) |
| `runtime_subscribers.py` | Connects task events to RuntimeState and RuntimeMemory | ✅ Stable |
| `logger.py` | Structured JSON file + stdout logging | ✅ Stable |
| `lifecycle.py` | TaskState enum (PENDING, RUNNING, SUCCESS, FAILED, RETRYING) | ✅ Stable |

**Authority:** The runtime module owns the task lifecycle. Nothing outside of it should mutate task state.

---

### 2.2 Intent Detection (`riya_engine/intent/`)

Two coexisting detectors — this is an overlap problem:

| File | Role | Status |
|---|---|---|
| `detector.py` (IntentDetector) | New runtime-compatible detector. Returns `IntentResponse` with `entities` dict | ✅ New / Active |
| `offline_intent.py` (detect_offline_intent) | Old-style detector. Returns `Intent` schema object with `.entity` | ⚠️ Old / Active via engine.py |
| `schema.py` (Intent) | Old intent model: `intent`, `entity`, `confidence`, `source` | ⚠️ Deprecated schema |
| `intent_response.py` (IntentResponse) | New intent model: `intent`, `confidence`, `entities` dict | ✅ New schema |

**Authority:** `detector.py` / `IntentResponse` is the canonical intent model for the new runtime. `schema.py` / `Intent` is legacy and must be retired.

---

### 2.3 Planner (`riya_engine/planner/`)

Two planners coexist — again a duplication problem:

| File | Role | Status |
|---|---|---|
| `planner.py` (Planner class) | New runtime-compatible. Takes `IntentResponse`, returns `[{capability, payload}]` steps | ✅ New / Active |
| `execution_planner.py` (build_execution_plan) | Old-style. Takes raw intent dict, returns `[{action, ...}]` steps | ⚠️ Old / Used by executor.py |

**Authority:** `planner.py` (Planner class) is the canonical planner. `execution_planner.py` must be retired once executor.py is removed.

---

### 2.4 Capability System (`riya_engine/capabilities/`)

| File | Role | Status |
|---|---|---|
| `registry.py` (CAPABILITY_REGISTRY) | Dict mapping capability name → execute function | ✅ Stable |
| `base_response.py` (CapabilityResponse) | Standardized return: `success`, `data`, `error` | ✅ Stable |
| `open_app.py` | Opens app via `subprocess.Popen`. Uses hardcoded path | ✅ Working (limited app list) |
| `close_app.py` | Closes app via `taskkill`. Uses hardcoded process names | ✅ Working (limited app list) |
| `app_control.py` | Old capability functions used by `executor.py`. Uses `os.system()` | ⚠️ Deprecated (old pipeline) |
| `capability_manager.py` | Old capability dispatcher used by `executor.py` | ⚠️ Deprecated |

**Authority:** `registry.py` + `open_app.py` + `close_app.py` + `base_response.py` form the canonical capability layer. `app_control.py` and `capability_manager.py` are legacy.

---

### 2.5 State Management (`riya_engine/state/`)

| File | Role | Status |
|---|---|---|
| `runtime_state.py` (RuntimeState) | Tracks active, completed, failed task dicts in memory | ✅ Stable |

**Problems:**
- `executor.py` imports `set_focus_mode` and `get_focus_mode` from `runtime_state.py`, but these functions **do not exist** in the current file. This is a dead import causing a crash if that path is hit.
- State is in-memory only — no persistence across restarts.
- No `session_id` or `request_id` grouping of tasks.

**Authority:** `RuntimeState` owns the live task ledger. It must not be written to by anything except `runtime_subscribers.py` (via events).

---

### 2.6 Memory Architecture (`riya_engine/memory/`)

Riya has **three separate memory systems** with overlapping responsibilities:

| File | Role | Mechanism | Status |
|---|---|---|---|
| `runtime_memory.py` (RuntimeMemory) | Append-only execution event log | In-memory list | ✅ New / Active |
| `context_memory.py` | Single global `_last_entity` variable | Module-level global | ⚠️ Fragile |
| `context.py` (ContextManager) | Per-session `last_intent` + `last_entity` + pronoun resolution | In-memory object | ⚠️ Underused |
| `memory_manager.py` | Persistent facts + conversation history | JSON file (`memory_store.json`) | ⚠️ Old pipeline only |
| `session_manager.py` | Save/restore named app sessions | JSON file (`sessions.json`) | ✅ Working (old pipeline) |

**Problems:**
- `context_memory.py` is a bare module-level global — not thread-safe, no scoping, no session isolation.
- `context.py` (ContextManager) and `context_memory.py` solve the same problem differently. Only one should exist.
- `memory_manager.py` is only used by the old pipeline. The new runtime has no persistent fact/learning memory.
- `session_manager.py` imports `remember_app` and `get_opened_apps` from `runtime_memory.py`, but those functions **do not exist** in the current `RuntimeMemory` class (it only has `remember()` and `get_history()`). This is a live bug.

---

### 2.7 NLP Layer (`riya_engine/nlp/`)

| File | Role | Status |
|---|---|---|
| `text_cleaner.py` | Strips filler words (please, hey, riya, etc.) | ✅ Stable |
| `command_splitter.py` | Splits "open X and close Y" into multiple commands | ✅ Stable |
| `conversation_cleaner.py` | Removes conversational padding | ✅ Stable |
| `entity_normalizer.py` | Maps app aliases to canonical names (e.g. "browser" → "chrome") | ✅ Stable |

**Problem:** The NLP layer is only used by `engine.py` (old pipeline). The new `core/main.py` pipeline passes raw input directly to `intent_detector.detect()` without any NLP preprocessing.

---

### 2.8 Voice Layer (`voice/`)

| File | Role | Status |
|---|---|---|
| `listener.py` | Speech-to-text stub | ⚠️ Stub (47 bytes) |
| `speech.py` | Text-to-speech stub | ⚠️ Stub (109 bytes) |

**Authority:** None currently. Voice is a future input channel — it must eventually feed the same intent pipeline as text input.

---

### 2.9 Personality System (`personality/`)

| File | Role | Status |
|---|---|---|
| `riya_personality.py` | Generates response text based on intent + personality state | ⚠️ Not connected to runtime |
| `behavior.py` | Behavior rules | ⚠️ Disconnected |
| `traits.py` | Personality traits constants | ⚠️ Disconnected |
| `state.py` | Returns current personality state | ⚠️ Disconnected |

**Problem:** The personality system generates response text but is **not called anywhere in the new runtime pipeline**. The new `core/main.py` prints raw debug output only. There is no response generation layer in the new pipeline.

---

### 2.10 Online Brain (`online/`)

| File | Role | Status |
|---|---|---|
| `online_brain.py` | Hardcoded keyword responses simulating an online AI | ⚠️ Stub |

**Authority:** None. The online brain is a placeholder with 3 hardcoded responses and no real LLM integration.

---

### 2.11 Router (`riya_engine/router.py`)

| File | Role | Status |
|---|---|---|
| `router.py` | Keyword-based offline/online routing | ⚠️ Old pipeline only |

**Problem:** The router is only used by the old `engine.py` pipeline. The new `core/main.py` does not route — it sends all input to the offline intent detector directly. There is no online fallback in the new pipeline.

---

## 3. Runtime Execution Flow

### 3.1 New Pipeline (core/main.py) — CORRECT PATH

```
User Input (text)
    │
    ▼
ExecutionContext(user_input)          ← creates request_id, session_id=None
    │
    ▼
IntentDetector.detect(text)           ← returns IntentResponse(intent, confidence, entities)
    │
    ├── UNKNOWN → print error, continue loop
    │
    ▼
Planner.create_plan(intent_response)  ← returns [{capability, payload}, ...]
    │
    ▼
[for each step]
TaskManager.create_task(capability, payload)
    │   └── emits TASK_CREATED → EventBus → runtime_subscribers (no handler for CREATED)
    ▼
Orchestrator.execute_task(task)
    │   ├── TaskManager.start_task()     → emits TASK_STARTED → RuntimeState + RuntimeMemory
    │   ├── CAPABILITY_REGISTRY[name](payload) → CapabilityResponse
    │   └── TaskManager.complete_task() → emits TASK_COMPLETED → RuntimeState + RuntimeMemory
    │       OR TaskManager.fail_task()  → emits TASK_FAILED → RuntimeState + RuntimeMemory
    ▼
Print: active_tasks, completed_tasks, failed_tasks, memory history
```

**Critical gap:** `ExecutionContext` is created but **never populated or used** — `set_intent()` and `set_plan()` are never called. It is dead scaffolding.

---

### 3.2 Old Pipeline (engine.py + executor.py) — LEGACY PATH

```
User Input (text)
    │
    ▼
router.route_input()         ← keyword match → "offline" or "online"
    │
    ▼ (offline)
engine.process(text)
    ├── clean_text()
    ├── conversational_clean()
    ├── split_commands()
    └── detect_offline_intent()   ← returns Intent(schema.py)
    │
    ▼
executor.execute(intent)
    ├── focus_mode path → build_execution_plan() → _run_planned_step()
    ├── save_session / restore_session → session_manager
    └── execute_capability(intent) → app_control.py functions
```

**This pipeline has a broken import:** `executor.py` imports `set_focus_mode, get_focus_mode` from `runtime_state.py` — functions that **do not exist**, making the focus_mode path crash.

---

## 4. Event-Driven Architecture

### Current Event Coverage

| Event | Emitter | Subscribers | Handler |
|---|---|---|---|
| `TASK_CREATED` | TaskManager | EventBus | None (no subscriber registered) |
| `TASK_STARTED` | TaskManager | runtime_subscribers | RuntimeState.add_active_task + RuntimeMemory.remember |
| `TASK_COMPLETED` | TaskManager | runtime_subscribers | RuntimeState remove/add_completed + RuntimeMemory.remember |
| `TASK_FAILED` | TaskManager | runtime_subscribers | RuntimeState remove/add_failed + RuntimeMemory.remember |
| `USER_INPUT_RECEIVED` | Nobody | Nobody | Defined in Events, never emitted |
| `INTENT_DETECTED` | Nobody | Nobody | Defined in Events, never emitted |
| `PLAN_CREATED` | Nobody | Nobody | Defined in Events, never emitted |
| `MEMORY_UPDATED` | Nobody | Nobody | Defined in Events, never emitted |
| `STATE_CHANGED` | Nobody | Nobody | Defined in Events, never emitted |
| `SYSTEM_ERROR` | Nobody | Nobody | Defined in Events, never emitted |

**Assessment:** The EventBus works correctly. The event taxonomy is well-designed. But 7 of 10 defined events are never emitted. The system is 30% wired. The pipeline stages (input, intent, plan) are completely outside the event system.

---

## 5. Architecture Overlap Problems

| Problem | Files Involved | Risk |
|---|---|---|
| Two intent detectors | `detector.py` (IntentResponse) vs `offline_intent.py` (Intent) | HIGH — incompatible schemas |
| Two intent schemas | `intent_response.py` vs `schema.py` | HIGH — breaks if mixed |
| Two planners | `planner.py` vs `execution_planner.py` | MEDIUM — different step formats |
| Two capability systems | `open_app.py`+`close_app.py`+`registry.py` vs `app_control.py`+`capability_manager.py` | HIGH — both open/close apps with different code paths |
| Two memory context systems | `context.py` vs `context_memory.py` | MEDIUM — same responsibility |
| Three memory systems total | RuntimeMemory + ContextMemory + MemoryManager | MEDIUM — no unified memory API |
| ExecutionContext created but never used | `core/main.py` | MEDIUM — wasted scaffolding |
| NLP preprocessing bypassed in new pipeline | `nlp/` vs `core/main.py` | HIGH — dirty text reaches intent detector |
| Personality system completely disconnected | `personality/` | LOW (currently) |
| Router only exists in old pipeline | `router.py` | LOW — but online fallback is missing |

---

## 6. Scalability Risks

| Risk | Description | Severity |
|---|---|---|
| No async execution | All tasks run synchronously in the main loop | HIGH |
| No task queue | Tasks execute immediately with no buffering or prioritization | HIGH |
| No session isolation | RuntimeState holds one global flat task list — no per-session grouping | HIGH |
| Global mutable state via module-level variables | `context_memory.py` uses `_last_entity` global | MEDIUM |
| No retry mechanism | `TaskState.RETRYING` is defined but never used | MEDIUM |
| Capability registry is a static dict | New capabilities require code changes to `registry.py` | MEDIUM |
| In-memory state only | RuntimeState and RuntimeMemory are lost on restart | HIGH |
| No input validation | No schema validation on capability payloads before execution | MEDIUM |
| Hard-coded app paths | `open_app.py` has one entry: chrome with a user-specific path | HIGH |

---

## 7. Missing Orchestration Layers

These layers are defined/partially scaffolded but not implemented:

| Missing Layer | What It Should Do | Current State |
|---|---|---|
| **Input Pipeline Integration** | NLP preprocessing before intent detection | NLP exists but bypassed |
| **ExecutionContext Propagation** | Context passed through intent → plan → tasks | Context created, never populated |
| **Response Generation Layer** | Convert task results to natural language | No response layer in new pipeline |
| **Session Management Layer** | Link requests to sessions, maintain session state | session_id is always None |
| **Online Routing Layer** | Fall back to online brain for non-offline intents | Router only in old pipeline |
| **Error Recovery Layer** | Handle failed tasks gracefully with fallback or retry | Fail and move on |
| **Async Task Queue** | Non-blocking task execution | Not present |
| **Capability Auto-Discovery** | Load capabilities without manual registry edits | Static dict |

---

## 8. Authority Boundaries (Subsystem Ownership)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 0: INPUT                                             │
│  Authority: voice/ (future) + core/main.py (current)       │
│  Owns: raw user input only                                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: NLP PREPROCESSING                                 │
│  Authority: riya_engine/nlp/                                │
│  Owns: text cleaning, splitting, entity normalization       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: INTENT DETECTION                                  │
│  Authority: riya_engine/intent/detector.py                  │
│  Owns: IntentResponse — intent name, confidence, entities   │
│  Must NOT: execute actions, access memory directly          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: PLANNING                                          │
│  Authority: riya_engine/planner/planner.py                  │
│  Owns: converting IntentResponse → ordered capability steps │
│  Must NOT: execute actions, know about tasks                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: RUNTIME (Task Lifecycle)                          │
│  Authority: riya_engine/runtime/orchestrator.py             │
│             riya_engine/runtime/task_manager.py             │
│  Owns: task creation, state transitions, event emission     │
│  Must NOT: directly modify state or memory                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: CAPABILITIES                                      │
│  Authority: riya_engine/capabilities/                       │
│  Owns: executing OS-level actions, returning CapabilityResponse │
│  Must NOT: manage tasks, emit events, touch memory          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: STATE + MEMORY (via Events only)                  │
│  Authority: riya_engine/state/runtime_state.py              │
│             riya_engine/memory/runtime_memory.py            │
│  Owns: read/write of runtime state and execution history    │
│  Must NOT: be written to except by runtime_subscribers.py   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 7: RESPONSE GENERATION                               │
│  Authority: personality/ (when connected)                   │
│  Owns: converting task results to natural language output   │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Stable vs Unstable Components

### ✅ Stable (production-safe)

- `runtime/event_bus.py` — Clean pub/sub, tested, working
- `runtime/task_manager.py` — Task lifecycle with events, working
- `runtime/orchestrator.py` — Registry lookup + execution, working
- `runtime/events.py` — Event constants, stable
- `runtime/lifecycle.py` — TaskState enum, stable
- `runtime/logger.py` — JSON structured logging to file, working
- `runtime/runtime_subscribers.py` — Event→State/Memory wiring, working
- `state/runtime_state.py` — Task ledger, working
- `capabilities/base_response.py` — CapabilityResponse contract, stable
- `capabilities/open_app.py` — Works (single app: chrome)
- `capabilities/close_app.py` — Works (single app: chrome)
- `capabilities/registry.py` — Static registry, stable
- `nlp/text_cleaner.py` — Stable
- `nlp/command_splitter.py` — Stable
- `nlp/entity_normalizer.py` — Stable
- `intent/intent_response.py` — New schema, stable
- `planner/planner.py` — New planner, stable

### ⚠️ Unstable / Incomplete

- `runtime/execution_context.py` — Created but never used in pipeline
- `intent/detector.py` — Works for chrome only (2 hardcoded rules)
- `memory/runtime_memory.py` — Missing `remember_app()`, `get_opened_apps()` methods that `app_control.py` and `session_manager.py` expect
- `memory/context_memory.py` — Bare module global, not session-safe
- `memory/context.py` — ContextManager not connected to any pipeline

### ❌ Deprecated (old pipeline, must be retired)

- `riya_engine/engine.py` — Old entry point
- `riya_engine/router.py` — Keyword-based offline/online router
- `riya_engine/execution/executor.py` — Old executor with broken imports
- `riya_engine/intent/offline_intent.py` — Old intent function
- `riya_engine/intent/schema.py` — Old Intent schema
- `riya_engine/planner/execution_planner.py` — Old planner function
- `riya_engine/capabilities/app_control.py` — Old capability functions
- `riya_engine/capabilities/capability_manager.py` — Old dispatcher
- `riya_engine/memory/memory_manager.py` — Old persistent memory

### 🔬 Experimental / Stub

- `voice/listener.py` — Empty stub
- `voice/speech.py` — Empty stub
- `online/online_brain.py` — 3 hardcoded responses
- `personality/` — Fully disconnected from runtime
- `riya_engine/modes/` — Empty (only `__init__.py`)

---

## 10. Recommended Migration Strategy

### Phase 1 — Fix Live Bugs (Immediate)

1. **Fix `runtime_memory.py`**: Add `remember_app(app_name)`, `get_opened_apps()`, and `clear_opened_apps()` methods to `RuntimeMemory` class so `session_manager.py` and `app_control.py` don't crash.
2. **Fix `executor.py` broken import**: Remove `set_focus_mode, get_focus_mode` from `runtime_state.py` import or add those methods — but since executor.py is deprecated, add a deprecation comment and leave it isolated.
3. **Fix `session_manager.py` unreachable code**: Lines 60–65 are dead code after a `return True` on line 56.

---

### Phase 2 — Wire NLP into New Pipeline

Currently `core/main.py` sends raw text straight to `intent_detector.detect()`. The NLP layer must be inserted:

```
user_input
  → clean_text()
  → conversational_clean()
  → split_commands()        ← produces list of command strings
  → [for each command] intent_detector.detect()
  → planner.create_plan()
  → task execution
```

This enables multi-command support and clean entity extraction.

---

### Phase 3 — Activate ExecutionContext

`ExecutionContext` must become the **carrier object** passed through the entire pipeline:

```python
context = ExecutionContext(user_input)
context.set_intent(intent_response)
context.set_plan(plan)
context.tasks = [task1, task2, ...]
```

This enables full request tracing, session linking, and future async queuing.

---

### Phase 4 — Emit All Events

Wire `USER_INPUT_RECEIVED`, `INTENT_DETECTED`, and `PLAN_CREATED` events into `core/main.py`. This gives full observability of the pipeline and allows any subsystem to react to any pipeline stage via subscriptions.

---

### Phase 5 — Unify Memory Architecture

Replace the three memory systems with a two-tier architecture:

- **Tier 1 — RuntimeMemory** (in-memory): execution events, active context, last entity — volatile, session-scoped.
- **Tier 2 — PersistentMemory** (JSON or SQLite): named sessions, user facts, conversation history — survives restarts.

Retire `context_memory.py` (bare global). Promote `context.py` (ContextManager) as the canonical context resolver, wire it into the new pipeline.

---

### Phase 6 — Retire Old Pipeline

Once the new pipeline fully handles all intents that the old pipeline handled, hard-delete:
- `riya_engine/engine.py`
- `riya_engine/router.py`
- `riya_engine/execution/executor.py`
- `riya_engine/intent/offline_intent.py`
- `riya_engine/intent/schema.py`
- `riya_engine/planner/execution_planner.py`
- `riya_engine/capabilities/app_control.py`
- `riya_engine/capabilities/capability_manager.py`
- `riya_engine/memory/memory_manager.py`

---

### Phase 7 — Connect Personality + Response Layer

Wire `personality/riya_personality.py` into the pipeline as Layer 7:

```python
# After task execution
response_text = generate_response(intent_response, task_results)
print(f"Riya: {response_text}")
```

---

### Phase 8 — Expand Capability Registry

Replace hardcoded app dicts in `open_app.py`/`close_app.py` with a `config/apps.json` file. Add capability auto-discovery so `registry.py` doesn't need manual edits for each new capability.

---

## 11. Recommended Next Development Priorities

| Priority | Task | Phase |
|---|---|---|
| 🔴 P0 | Fix `RuntimeMemory` missing methods (`remember_app`, `get_opened_apps`) | Phase 1 |
| 🔴 P0 | Fix broken import in `executor.py` (focus_mode crash) | Phase 1 |
| 🟠 P1 | Insert NLP preprocessing into `core/main.py` pipeline | Phase 2 |
| 🟠 P1 | Populate `ExecutionContext` through the pipeline | Phase 3 |
| 🟡 P2 | Emit `USER_INPUT_RECEIVED`, `INTENT_DETECTED`, `PLAN_CREATED` events | Phase 4 |
| 🟡 P2 | Expand `IntentDetector` beyond 2 hardcoded rules | Phase 4 |
| 🟡 P2 | Unify `context_memory.py` + `context.py` into one ContextManager | Phase 5 |
| 🟢 P3 | Retire old pipeline files | Phase 6 |
| 🟢 P3 | Connect personality/response layer | Phase 7 |
| 🟢 P3 | Expand capability registry (more apps, config-driven) | Phase 8 |
| 🔵 P4 | Add async task execution | Post-stabilization |
| 🔵 P4 | Add session persistence to RuntimeState | Post-stabilization |
| 🔵 P4 | Voice layer integration | Riya V3 prep |
| 🔵 P4 | Real LLM online brain | Riya V3 prep |

---

## 12. Summary: Architecture Health Score

| Subsystem | Health |
|---|---|
| Runtime Core (EventBus, TaskManager, Orchestrator) | 🟢 Good |
| Capability System (new) | 🟡 Working, limited |
| Intent Detection (new) | 🟡 Working, minimal |
| Planner (new) | 🟡 Working, minimal |
| State Management | 🟡 Working, no persistence |
| Memory Architecture | 🔴 Fragmented, broken imports |
| NLP Layer | 🔴 Bypassed in new pipeline |
| ExecutionContext | 🔴 Dead scaffolding |
| Event Coverage | 🟡 30% wired |
| Old Pipeline Cleanup | 🔴 Not started |
| Response Generation | 🔴 Missing entirely |
| Voice / Online / Personality | 🔴 Disconnected stubs |

**Overall:** The runtime foundation is solid. The critical next step is completing the new pipeline wiring and retiring the old one.
