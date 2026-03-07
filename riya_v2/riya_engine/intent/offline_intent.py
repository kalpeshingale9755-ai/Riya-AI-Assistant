from riya_engine.intent.schema import Intent


APP_KEYWORDS = ["open", "launch", "start", "run"]


def detect_offline_intent(text: str):
    text = text.lower()

    words = text.split()

    # detect open app intent
    for keyword in APP_KEYWORDS:
        if keyword in words:
            # assume next word is app name (simple logic)
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

    # detect close app intent
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




    # fallback intent
    return Intent(
        intent="unknown",
        entity=None,
        confidence=0.2,
        source="offline",
    )