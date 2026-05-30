# riya_engine/intent/detector.py

from riya_engine.intent.intent_response import IntentResponse

from riya_engine.memory.context_memory import context_memory

from riya_engine.memory.memory_orchestrator import memory




class IntentDetector:

    def detect(self, text):

        text = text.lower()

        # ==========================================
        # OPEN APP
        # ==========================================

        if text.startswith("open"):

            if "chrome" in text:

                return IntentResponse(
                    intent="OPEN_APP",
                    confidence=0.95,
                    entities={
                        "app_name": "chrome"
                    }
                )

        # ==========================================
        # CLOSE APP
        # ==========================================

        if text.startswith("close"):

            # --------------------------------------
            # DIRECT APP NAME
            # --------------------------------------

            if "chrome" in text:

                return IntentResponse(
                    intent="CLOSE_APP",
                    confidence=0.95,
                    entities={
                        "app_name": "chrome"
                    }
                )

            # --------------------------------------
            # CONTEXTUAL ENTITY RESOLUTION
            # --------------------------------------

            if "it" in text:

                entity = memory.get_last_entity()

                if entity:

                    if entity["type"] == "app":

                        return IntentResponse(
                            intent="CLOSE_APP",
                            confidence=0.90,
                            entities={
                                "app_name": entity["value"]
                            }
                        )

        # ==========================================
        # SEARCH YOUTUBE
        # ==========================================

        if "search youtube" in text:

            query = text.replace(
                "search youtube",
                ""
            ).strip()

            return IntentResponse(
                intent="SEARCH_YOUTUBE",
                confidence=0.95,
                entities={
                    "query": query
                }
            )

        # ==========================================
        # UNKNOWN
        # ==========================================

        return IntentResponse(
            intent="UNKNOWN",
            confidence=0.0,
            entities={}
        )


intent_detector = IntentDetector()