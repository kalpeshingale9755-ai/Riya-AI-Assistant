# riya_engine/nlp/text_cleaner.py

FILLER_WORDS = [
    "please",
    "can",
    "could",
    "you",
    "hey",
    "riya",
    "for",
    "me",
    "would",
    "kindly",
    "just",
]


def clean_text(text: str) -> str:
    text = text.lower()
    words = text.split()

    cleaned_words = [
        word for word in words if word not in FILLER_WORDS
    ]

    return " ".join(cleaned_words)