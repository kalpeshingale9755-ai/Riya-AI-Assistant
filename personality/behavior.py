from personality.state import set_state


def update_state(route, intent=None):
    """
    Decide personality mode automatically.
    """

    # Online conversation → friendly
    if route == "online":
        set_state("friendly")
        return

    # Offline commands
    if intent:
        if intent.intent in ["open_app", "close_app"]:
            set_state("focused")
        else:
            set_state("assistant")