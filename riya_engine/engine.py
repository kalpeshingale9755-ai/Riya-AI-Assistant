from riya_engine.intent.offline_intent import detect_offline_intent
from riya_engine.memory.context import context_manager


def process(text):
    print(f"[Engine] Processing input: {text}")

    intent = detect_offline_intent(text)

    # resolve entity
    resolved_entity = context_manager.resolve_pronoun(intent.entity)
    intent.entity = resolved_entity

    # update memory only if entity exists
    if intent.entity:
        context_manager.update(intent)

    return intent