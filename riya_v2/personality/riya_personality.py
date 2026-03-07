from personality.traits import RIYA_TRAITS
from personality.state import get_state


def generate_response(intent):
    print("[Personality] Generating response")

    action = intent.intent
    entity = intent.entity
    mode = get_state()

    name = RIYA_TRAITS["name"]

    # ---- Assistant Mode (default) ----
    if mode == "assistant":
        if action == "open_app" and entity:
            return f"{name} is opening {entity}."
        if action == "close_app" and entity:
            return f"{name} is closing {entity}."

    # ---- Focused Mode ----
    if mode == "focused":
        if entity:
            return f"Opening {entity}."

    # ---- Friendly Mode ----
    if mode == "friendly":
        if entity:
            return f"Sure, opening {entity} for you."

    if action == "unknown":
        return "I'm not fully sure yet, but I'm learning."

    return "Task completed."