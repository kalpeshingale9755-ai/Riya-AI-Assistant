# riya_engine/capabilities/capability_manager.py

from .app_control import open_app, close_app, close_all_apps
from riya_engine.memory.context_memory import set_last_entity

from .open_url import execute as open_url

from .search_youtube import execute as search_youtube




def execute_capability(intent):
    print(f"[capability] Executing intent: {intent.__dict__}")

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

    elif intent.intent == "open_url":
        return open_url({"url": intent.entities.get("url")})

    elif intent.intent == "search_youtube":
        return search_youtube({"query": intent.entities.get("query")})

    return False