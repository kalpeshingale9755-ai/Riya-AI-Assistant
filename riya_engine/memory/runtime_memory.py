# runtime_memory.py

OPENED_APPS = set()


def remember_opened_app(app_name: str):
    OPENED_APPS.add(app_name)
    print(f"[RuntimeMemory] Remembered: {app_name}")


def forget_app(app_name: str):
    OPENED_APPS.discard(app_name)
    print(f"[RuntimeMemory] Removed: {app_name}")


def get_opened_apps():
    return list(OPENED_APPS)