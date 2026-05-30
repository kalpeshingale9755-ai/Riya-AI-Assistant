# test_runtime.py

from riya_engine.runtime.event_bus import event_bus
from riya_engine.runtime.events import Events

from riya_engine.runtime.task_manager import task_manager

from riya_engine.runtime.execution_context import ExecutionContext

from riya_engine.runtime.orchestrator import orchestrator

from riya_engine.intent.detector import intent_detector

from riya_engine.planner.planner import planner


# ==========================================
# EVENT LISTENERS
# ==========================================

def on_task_created(data):

    print("\n[LISTENER] TASK CREATED")
    print(data)


def on_task_started(data):

    print("\n[LISTENER] TASK STARTED")
    print(data)


def on_task_completed(data):

    print("\n[LISTENER] TASK COMPLETED")
    print(data)


def on_task_failed(data):

    print("\n[LISTENER] TASK FAILED")
    print(data)


# ==========================================
# SUBSCRIBE EVENTS
# ==========================================

event_bus.subscribe(
    Events.TASK_CREATED,
    on_task_created
)

event_bus.subscribe(
    Events.TASK_STARTED,
    on_task_started
)

event_bus.subscribe(
    Events.TASK_COMPLETED,
    on_task_completed
)

event_bus.subscribe(
    Events.TASK_FAILED,
    on_task_failed
)


# ==========================================
# USER INPUT
# ==========================================

user_input = "open chrome"


# ==========================================
# EXECUTION CONTEXT
# ==========================================

context = ExecutionContext(
    user_input=user_input
)


# ==========================================
# INTENT DETECTION
# ==========================================

intent_response = intent_detector.detect(
    user_input
)

print("\n========== INTENT ==========")

print(intent_response.to_dict())


# ==========================================
# PLAN GENERATION
# ==========================================

plan = planner.create_plan(
    intent_response
)

print("\n========== PLAN ==========")

print(plan)


# ==========================================
# TASK EXECUTION
# ==========================================

for step in plan:

    task = task_manager.create_task(
        capability_name=step["capability"],
        payload=step["payload"]
    )

    orchestrator.execute_task(task)


print("\n========== EXECUTION COMPLETE ==========")