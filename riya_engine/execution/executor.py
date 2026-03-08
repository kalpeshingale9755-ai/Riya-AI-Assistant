from riya_engine.capabilities.capability_manager import execute_capability


def execute(intent):
    print("[TRACE] executor reached")
    
    print(f"[Executor] Executing intent: {intent}")

    result = execute_capability(intent)

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

    return result