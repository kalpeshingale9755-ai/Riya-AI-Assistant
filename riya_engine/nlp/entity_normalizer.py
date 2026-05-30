APP_ALIASES = {
    "chrome":  ["chrome", "google chrome", "chrome browser", "browser"],
    "notepad": ["notepad", "text editor", "notepad.exe"],
    "vscode":  ["vscode", "visual studio code", "vs code", "code editor", "code"],
    "youtube": ["youtube", "yt"],
}


def normalize_app_name(phrase: str):
    """
    Map a raw app phrase to its canonical name using APP_ALIASES.
    Returns the canonical name if found, the raw phrase if not,
    or None for empty input.
    """
    if not phrase:
        return None

    phrase = phrase.lower().strip()

    for canonical, aliases in APP_ALIASES.items():
        if phrase in aliases:
            return canonical

    # Not in aliases — pass through so open_app can fail gracefully
    return phrase


def normalize_entities(text):

    replacements = {

        "google chrome": "chrome",

        "chrome browser": "chrome"

    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text