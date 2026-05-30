# riya_engine/nlp/pipeline.py

from riya_engine.nlp.text_cleaner import clean_text

from riya_engine.nlp.command_splitter import split_commands

from riya_engine.nlp.entity_normalizer import normalize_entities

from riya_engine.runtime.event_bus import event_bus

from riya_engine.runtime.event_types import *





class NLPPipeline:

    def process(self, text):

        # ==========================================
        # CLEAN TEXT
        # ==========================================

        cleaned_text = clean_text(text)


        event_bus.emit(
            TEXT_CLEANED,
            {
                "cleaned_text": cleaned_text
            }
        )

        # ==========================================
        # SPLIT COMMANDS
        # ==========================================

        commands = split_commands(cleaned_text)

        processed_commands = []

        event_bus.emit(
            COMMAND_SPLIT,
            {
                "commands": commands
            }
        )

        # ==========================================
        # NORMALIZE EACH COMMAND
        # ==========================================

        for command in commands:

            normalized_command = normalize_entities(
                command
            )

            processed_commands.append(
                normalized_command
            )

            event_bus.emit(
                ENTITY_NORMALIZED,
                {
                    "normalized_command": normalized_command
                }
            )

        return processed_commands


nlp_pipeline = NLPPipeline()

