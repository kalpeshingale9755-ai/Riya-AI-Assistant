class Intent:
    def __init__(self, intent, entity=None, confidence=0.0, source="offline"):
        self.intent = intent
        self.entity = entity
        self.confidence = confidence
        self.source = source

    def to_dict(self):
        return {
            "intent": self.intent,
            "entity": self.entity,
            "confidence": self.confidence,
            "source": self.source,
        }

    def __str__(self):
        return str(self.to_dict())