def think_online(text):
    print("[Online Brain] Thinking...")

    text_lower = text.lower()

    # recognize known user
    if "user name is" in text_lower and "hello" in text_lower:
        name = text_lower.split("user name is")[-1].split(".")[0].strip()
        return f"Welcome back {name.capitalize()}."

    if "how am i" in text_lower:
        return "You seem curious today. I'm here with you."

    return "That's interesting. Tell me more."