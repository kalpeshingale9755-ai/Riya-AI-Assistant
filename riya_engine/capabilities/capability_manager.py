# riya_engine/capabilities/capability_manager.py

from .app_control import open_app, close_app, close_all_apps


def execute_capability(intent):
    print("[TRACE] capability manager")

    action = intent.intent
    entity = intent.entity

    if action == "open_app":
        return open_app(entity)

    if action == "close_app":
        return close_app(entity)

    if action == "close_all_apps":
        return close_all_apps()

    return False