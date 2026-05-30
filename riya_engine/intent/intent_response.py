# riya_engine/intent/intent_response.py

class IntentResponse:

    def __init__(
        self,
        intent,
        confidence,
        entities=None
    ):

        self.intent = intent

        self.confidence = confidence

        self.entities = entities or {}

    def to_dict(self):

        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "entities": self.entities
        }