import re
from config import WAKE_WORDS

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def is_wake_word(text):
    text = normalize_text(text)

    for wake in WAKE_WORDS:
        wake = normalize_text(wake)

        # exact phrase match
        if text == wake:
            return True

        # phrase inside sentence but word-safe
        if f" {wake} " in f" {text} ":
            return True

    return False
