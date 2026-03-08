class ContextManager:
    def __init__(self):
        self.last_intent = None
        self.last_entity = None

    def update(self, intent_obj):
        self.last_intent = intent_obj.intent
        self.last_entity = intent_obj.entity

    def resolve_pronoun(self, entity):
        if entity is None:
            return self.last_entity

        if entity.lower() in ["it", "this", "that"]:
            return self.last_entity



        return entity


# create global session context
context_manager = ContextManager()