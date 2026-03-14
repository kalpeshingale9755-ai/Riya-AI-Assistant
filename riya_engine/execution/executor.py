from riya_engine.capabilities.capability_manager import execute_capability
from riya_engine.memory.context_memory import set_last_entity
from riya_engine.capabilities.app_control import (
    open_app,
    close_app,
    close_all_apps
)



def execute(intent):
    print("[TRACE] executor reached >>> EXEC CALLED")
    
    print(f"[Executor] Executing intent: {intent}")

    

    if intent.intent == "save_session":
        from riya_engine.memory.session_manager import save_current_session
        save_current_session(intent.entity)

    elif intent.intent == "restore_session":
        from riya_engine.memory.session_manager import restore_session
        restore_session(intent.entity)


    elif intent.intent == "focus_mode":
        from riya_engine.capabilities.app_control import close_all_apps
        from riya_engine.memory.session_manager import restore_session

        print("[Focus Mode] Preparing workspace")

        close_all_apps()
        restore_session(intent.entity)

    if intent.entity:
        set_last_entity(intent.entity)

    
    result = execute_capability(intent)


    return result