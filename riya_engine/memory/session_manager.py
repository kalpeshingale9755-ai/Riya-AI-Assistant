import json
from pathlib import Path
from riya_engine.memory.runtime_memory import get_opened_apps
from datetime import datetime
from riya_engine.capabilities.app_control import open_app
from riya_engine.memory.runtime_memory import (
    get_opened_apps,
    clear_opened_apps
)

SESSION_FILE = Path(__file__).parent / "sessions.json"


def load_sessions():
    if not SESSION_FILE.exists():
        return {}

    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)


def save_session(name, apps):
    sessions = load_sessions()

    sessions[name] = {
        "apps": apps,
        "hour": datetime.now().hour
    }

    save_sessions(sessions)
    print(f"[Session] Saved session: {name}")


def get_session(name):
    sessions = load_sessions()
    return sessions.get(name)


def save_current_session(name):
    apps = get_opened_apps()

    if not apps:
        print("[Session] No active apps to save")
        return False

    save_session(name, apps)

    # ⭐ NEW — reset workspace memory
    # clear_opened_apps()

    return True



    if not apps:
        print("[Session] No active apps to save")
        return False

    save_session(name, apps)
    return True


def restore_session(name):

    session = get_session(name)

    if not session:
        print("[Session] Session not found")
        return False

    print(f"[Session] Restoring: {name}")

    for app in session["apps"]:
        open_app(app)

    return True