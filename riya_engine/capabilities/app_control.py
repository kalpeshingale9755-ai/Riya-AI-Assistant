import os
import subprocess
from riya_engine.memory.runtime_memory import remember_app
from riya_engine.memory.runtime_memory import get_opened_apps


APPS = {
    "chrome": {
        "open": "start chrome",
        "process": "chrome.exe"
    },
    "notepad": {
        "open": "start notepad",
        "process": "notepad.exe"
    },
    "calculator": {
        "open": "start calc",
        "process": "CalculatorApp.exe"
    }
}


def open_app(app_name: str):
    app = APPS.get(app_name.lower())

    if not app:
        return False

    print(f"[Capability] Opening {app_name}")
    os.system(app["open"])
    remember_app(app_name)
    return True


def close_app(app_name: str):
    app = APPS.get(app_name.lower())

    if not app:
        return False

    print(f"[Capability] Closing {app_name}")
    os.system(f'taskkill /IM {app["process"]} /F')
    return True



def is_running(process_name):
    """Check if process is currently running"""
    result = subprocess.run(
        ["tasklist"],
        capture_output=True,
        text=True
    )
    return process_name.lower() in result.stdout.lower()


def close_all_apps():
    print("[Capability] Smart closing Riya-opened apps")

    opened_apps = get_opened_apps()

    if not opened_apps:
        print("[Capability] No apps opened by Riya")
        return False

    for app_name in opened_apps:
        app = APPS.get(app_name)
        if app:
            process = app["process"]
            print(f"[Capability] Closing {app_name}")
            os.system(f'taskkill /IM {process} /F')

    return True


