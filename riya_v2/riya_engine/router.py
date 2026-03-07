def route_input(text):
    """
    Decide whether input should use
    offline engine or online intelligence.
    """

    offline_keywords = [
        "open",
        "close",
        "shutdown",
        "time",
        "date",
        "play",
        "pause",
        "volume",
        "music"
]

    text_lower = text.lower()

    for word in offline_keywords:
        if word in text_lower:
            return "offline"

    return "online"