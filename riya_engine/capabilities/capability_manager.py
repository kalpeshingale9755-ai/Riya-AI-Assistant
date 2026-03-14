# riya_engine/capabilities/capability_manager.py

from .app_control import open_app, close_app, close_all_apps
from riya_engine.memory.context_memory import set_last_entity

def execute_capability(intent):
    print(f"[Executor] Executing intent: {intent.__dict__}")

    if intent.intent == "open_app":
        open_app(intent.entity)
        set_last_entity(intent.entity)   # ⭐ NEW
        return True

    elif intent.intent == "close_app":
        close_app(intent.entity)
        set_last_entity(intent.entity)   # ⭐ NEW
        return True

    elif intent.intent == "close_all_apps":
        close_all_apps()
        return True

    return False