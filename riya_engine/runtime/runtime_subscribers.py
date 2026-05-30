# riya_engine/runtime/runtime_subscribers.py

from riya_engine.runtime.event_bus import event_bus

from riya_engine.runtime.events import Events

from riya_engine.state.runtime_state import runtime_state

from riya_engine.memory.runtime_memory import runtime_memory

from riya_engine.memory.memory_orchestrator import memory


# ==========================================
# TASK STARTED
# ==========================================

def handle_task_started(task):

    runtime_state.add_active_task(task)

    runtime_memory.remember(
        Events.TASK_STARTED,
        task
    )


# ==========================================
# TASK COMPLETED
# ==========================================

def handle_task_completed(task):

    runtime_state.remove_active_task(
        task["task_id"]
    )

    runtime_state.add_completed_task(task)

    # Persist the task to runtime memory.
    memory.store_task(task)

    # Post-completion: propagate entity/action context from result data.
    # This is the correct place to do it — after the orchestrator has
    # confirmed success and committed the result.
    result_data = task.get("result", {}).get("data", {})

    if "app" in result_data:

        memory.store_entity(
            {
                "type": "app",
                "value": result_data["app"]
            }
        )

        memory.store_action(
            task.get('capability', '').upper()
        )

    runtime_memory.remember(
        Events.TASK_COMPLETED,
        task
    )


# ==========================================
# TASK FAILED
# ==========================================

def handle_task_failed(task):

    runtime_state.remove_active_task(
        task["task_id"]
    )

    runtime_state.add_failed_task(task)

    runtime_memory.remember(
        Events.TASK_FAILED,
        task
    )


# ==========================================
# EVENT SUBSCRIPTIONS
# ==========================================

event_bus.subscribe(
    Events.TASK_STARTED,
    handle_task_started
)

event_bus.subscribe(
    Events.TASK_COMPLETED,
    handle_task_completed
)

event_bus.subscribe(
    Events.TASK_FAILED,
    handle_task_failed
)