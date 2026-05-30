APP_ALIASES = {
    "chrome": ["chrome", "google chrome", "chrome browser", "browser"],
    "notepad": ["notepad", "text editor"],
    "vscode": ["vscode", "visual studio code", "code editor"],
    "youtube": ["youtube", "yt"],
}



def normalize_entities(text):

    replacements = {

        "google chrome": "chrome",

        "chrome browser": "chrome"

    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text