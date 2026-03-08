from personality.traits import RIYA_TRAITS
from personality.state import get_state


def generate_response(intent):
    print("[Personality] Generating response")

    state = get_state()   # ⭐ get current personality mode

    action = intent.intent
    entity = intent.entity

    # ---------- FRIENDLY MODE ----------
    if state == "friendly":
        if action == "open_app":
            return f"Sure 😊 Opening {entity}."
        elif action == "close_app":
            return f"Okay 👍 Closing {entity}."

    # ---------- FOCUSED MODE ----------
    elif state == "focused":
        if action == "open_app":
            return f"Opening {entity}."
        elif action == "close_app":
            return f"Closing {entity}."




    elif action == "save_session":
        return f"Session {entity} saved."

    elif action == "restore_session":
        return f"Restoring session {entity}."
    
    elif action == "focus_mode":
        return f"Entering focus mode for {entity}."



    # ---------- DEFAULT ----------
    if action == "unknown":
        return "I'm not sure how to help with that yet."

    return "Done."