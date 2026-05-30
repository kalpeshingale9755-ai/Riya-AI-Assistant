from riya_engine.intent.offline_intent import detect_offline_intent
from riya_engine.memory.context import context_manager
from riya_engine.nlp.text_cleaner import clean_text
from riya_engine.nlp.command_splitter import split_commands
from riya_engine.nlp.conversation_cleaner import conversational_clean

def process(text):
    print(f"[Engine] Raw input: {text}")

    text = clean_text(text)
    text = conversational_clean(text)
    
    print(f"[Engine] Cleaned input: {text}")

    commands = split_commands(text)

    intents = []

    for cmd in commands:
        result = detect_offline_intent(cmd)

        if isinstance(result, list):
            intents.extend(result)
        else:
            intents.append(result)

    return intents