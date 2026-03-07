def route_input(text):
    """
    Decide whether input should use
    offline engine or online intelligence.
    """

    offline_keywords = [
        "open",  "close",  "shutdown",  "time",  "date",  "play",
        "pause",  "volume",  "music",  "save",  "restore",  "focus"
    ]

    text_lower = text.lower()

    # ⭐ SESSION COMMANDS MUST BE OFFLINE
    if text_lower.startswith("save session") or text_lower.startswith("restore session") or text_lower.startswith("focus"):
        return "offline"

    for word in offline_keywords:
        if word in text_lower:
            return "offline"

    return "online"