CURRENT_STATE = {
    "mode": "assistant"
}


def set_state(mode):
    CURRENT_STATE["mode"] = mode


def get_state():
    return CURRENT_STATE["mode"]