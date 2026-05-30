from riya_engine.intent.schema import Intent
from riya_engine.memory.context_memory import get_last_entity
from riya_engine.nlp.entity_normalizer import normalize_app_name



OPEN_KEYWORDS = ["open", "launch", "start", "run"]
IGNORE_WORDS = ["and", "then", "please", "app", "the"]

def detect_offline_intent(text: str):
    text = text.lower()
    words = text.split()

    # -------------------------
    # FOCUS MODE (FIXED)
    # -------------------------
    if "focus" in words:

        try:
            index = words.index("focus")

            # support: "focus mode study"
            if len(words) > index + 2 and words[index + 1] == "mode":
                session = words[index + 2]

            # support: "focus study"
            else:
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


    # ⭐ reopen previous app
    if "open it again" in text or "open again" in text:
        return Intent(
            intent="open_app",
            entity=get_last_entity(),
            confidence=0.9,
            source="offline",
        )


    # OPEN APP (multi-entity support)
    for keyword in OPEN_KEYWORDS:
        if keyword in words:
            index = words.index(keyword)
            app_phrase = " ".join(words[index + 1:])

            app_phrase = " ".join(
                w for w in app_phrase.split()
                if w not in IGNORE_WORDS
            )

            normalized_app = normalize_app_name(app_phrase)

            return [
                Intent(
                    intent="open_app",
                    entity=normalized_app,
                    confidence=0.8,
                    source="offline",
                )
            ]

    
    # CLOSE APP
    CLOSE_KEYWORDS = ["close", "exit", "quit", "stop"]

    for keyword in CLOSE_KEYWORDS:
        if keyword in words:
            index = words.index(keyword)

            # build phrase after keyword
            app_phrase = " ".join(words[index + 1:])

            # remove filler words
            app_phrase = " ".join(
                w for w in app_phrase.split()
                if w not in IGNORE_WORDS
            )

            normalized_app = normalize_app_name(app_phrase)

            # ⭐ ENTITY RESOLUTION (single source of truth)
            if normalized_app in ["", None, "it", "that", "again", "app", "application"]:
                last_entity = get_last_entity()
                print(f"[DEBUG] Using memory entity: {last_entity}")

                if not last_entity:
                    return Intent("unknown", None, 0.2, "offline")

                normalized_app = last_entity

            return [
                Intent(
                    intent="close_app",
                    entity=normalized_app,
                    confidence=0.8,
                    source="offline",
                )
            ]