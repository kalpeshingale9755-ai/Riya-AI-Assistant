# runtime_memory.py

# Runtime workspace memory

# ⭐ GLOBAL WORKSPACE STATE
opened_apps = []


def remember_app(app_name):
    if app_name and app_name not in opened_apps:
        opened_apps.append(app_name)
        print(f"[RuntimeMemory] Remembered: {app_name}")


def get_opened_apps():
    return opened_apps.copy()


def clear_opened_apps():
    opened_apps.clear()
    print("[RuntimeMemory] Cleared opened apps")