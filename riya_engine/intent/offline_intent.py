from riya_engine.intent.schema import Intent

APP_KEYWORDS = ["open", "launch", "start", "run"]

def detect_offline_intent(text: str):
    text = text.lower()
    words = text.split()

    # FOCUS MODE
    if "focus" in words:
        try:
            index = words.index("focus")
            session = words[index + 1]
        except IndexError:
            session = "default"

        return Intent(
            intent="focus_mode",
            entity=session,
            confidence=0.9,
            source="offline"
        )

    # SAVE SESSION
    if text.startswith("save session"):
        name = text.replace("save session", "").strip() or "default"
        return Intent("save_session", name, 0.9, "offline")

    # RESTORE SESSION
    if text.startswith("restore session"):
        name = text.replace("restore session", "").strip() or "default"
        return Intent("restore_session", name, 0.9, "offline")

    # CLOSE ALL APPS
    if "close all" in text:
        return Intent(
            intent="close_all_apps",
            entity=None,
            confidence=0.9,
            source="offline",
        )

    # OPEN APP
    for keyword in APP_KEYWORDS:
        if keyword in words:
            try:
                index = words.index(keyword)
                app_name = words[index + 1]
            except IndexError:
                app_name = None

            return Intent(
                intent="open_app",
                entity=app_name,
                confidence=0.7,
                source="offline",
            )

    CLOSE_KEYWORDS = ["close", "exit", "quit", "stop"]

    # CLOSE APP
    for keyword in CLOSE_KEYWORDS:
        if keyword in words:
            try:
                index = words.index(keyword)
                app_name = words[index + 1]
            except IndexError:
                app_name = None

            return Intent(
                intent="close_app",
                entity=app_name,
                confidence=0.7,
                source="offline",
            )

    # FALLBACK
    return Intent(
        intent="unknown",
        entity=None,
        confidence=0.2,
        source="offline",
    )