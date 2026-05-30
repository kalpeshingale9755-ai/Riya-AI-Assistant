from riya_engine.capabilities.capability_manager import execute_capability
from riya_engine.memory.context_memory import set_last_entity
from riya_engine.capabilities.app_control import (
    close_all_apps
)
from riya_engine.state.runtime_state import (
    set_focus_mode,
    get_focus_mode,
)
from riya_engine.planner import build_execution_plan


def _run_planned_step(step, fallback_entity=None):
    action = step.get("action")

    if action == "save_session":
        from riya_engine.memory.session_manager import save_current_session
        session_name = step.get("name") or fallback_entity or "default"
        return save_current_session(session_name)

    if action == "close_all_apps":
        return close_all_apps()

    if action == "restore_session":
        from riya_engine.memory.session_manager import restore_session
        session_name = step.get("name") or fallback_entity or "default"
        return restore_session(session_name)

    return False




def execute(intent):
    print("[TRACE] executor reached >>> EXEC CALLED")
    
    print(f"[Executor] Executing intent: {intent}")

    

    if intent.intent == "focus_mode":
        current_mode = get_focus_mode()

        # Prevent duplicate activation
        if current_mode == intent.entity:
            print(f"[Executor] Already in '{current_mode}' focus mode.")
            return

        print("[Focus Mode] Planning workspace steps")
        plan = build_execution_plan({
            "intent": intent.intent,
            "entity": intent.entity,
        })

        for step in plan:
            _run_planned_step(step, fallback_entity=intent.entity)

        # save active state
        set_focus_mode(intent.entity)

        if intent.entity:
            set_last_entity(intent.entity)

        return True

    if intent.intent == "save_session":
        from riya_engine.memory.session_manager import save_current_session
        save_current_session(intent.entity)

    elif intent.intent == "restore_session":
        from riya_engine.memory.session_manager import restore_session
        restore_session(intent.entity)

    if intent.entity:
        set_last_entity(intent.entity)

    
    result = execute_capability(intent)


    return result