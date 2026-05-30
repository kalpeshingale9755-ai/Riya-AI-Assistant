FILLER_WORDS = {
    "can", "you", "please", "could", "would",
    "hey", "riya", "for", "me", "the",
    "a", "an", "to", "i", "want", "need", "now"
}

def conversational_clean(text: str) -> str:
    words = text.lower().split()

    filtered = [
        w for w in words
        if w not in FILLER_WORDS
    ]

    return " ".join(filtered)