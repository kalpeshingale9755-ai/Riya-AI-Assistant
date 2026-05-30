# riya_engine/memory/context_memory.py


class ContextMemory:

    def __init__(self):

        self._last_entity = None

        self._last_action = None

    # ==========================================
    # ENTITY
    # ==========================================

    def set_last_entity(self, entity: dict):

        if entity:
            self._last_entity = entity
            print(f"[Context] Last entity set to: {entity}")

    def get_last_entity(self):

        return self._last_entity

    # ==========================================
    # ACTION
    # ==========================================

    def set_last_action(self, action: str):

        if action:
            self._last_action = action
            print(f"[Context] Last action set to: {action}")

    def get_last_action(self):

        return self._last_action

    # ==========================================
    # CLEAR
    # ==========================================

    def clear_context(self):

        self._last_entity = None
        self._last_action = None


# global singleton
context_memory = ContextMemory()