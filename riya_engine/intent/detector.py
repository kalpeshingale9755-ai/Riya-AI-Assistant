# riya_engine/intent/detector.py

from riya_engine.intent.intent_response import IntentResponse

from riya_engine.memory.memory_orchestrator import memory

from riya_engine.nlp.entity_normalizer import normalize_app_name


# ---------------------------------------------------------------------------
# Keyword sets
# ---------------------------------------------------------------------------

_OPEN_KEYWORDS  = {"open", "launch", "start", "run"}
_CLOSE_KEYWORDS = {"close", "exit", "quit", "stop"}

# Phrases that indicate "close the last app I used" rather than a named app
_CONTEXTUAL_REFS = {"it", "that", "app", "application", "this", ""}

# Words stripped from app phrases before normalization
_FILLER_WORDS = {"and", "the", "please", "a", "an"}

# Trigger prefixes that unambiguously mean "open a URL"
_URL_PREFIXES = ("go to ", "visit ", "open url ")


def _extract_url(words):
    """Return the first http/https token from a word list, or None."""
    for w in words:
        if w.startswith("http://") or w.startswith("https://"):
            return w
    return None


class IntentDetector:

    def detect(self, text):

        text  = text.lower().strip()
        words = text.split()

        if not words:
            return IntentResponse(intent="UNKNOWN", confidence=0.0, entities={})

        first = words[0]

        # ==========================================
        # OPEN URL
        # Checked before OPEN_APP so that
        # "open https://..." is not treated as an
        # app-open command.
        # Triggers:
        #   • any word starting with http:// or https://
        #   • "go to <url>"
        #   • "visit <url>"
        #   • "open url <url>"
        # ==========================================

        url = _extract_url(words)

        if url:
            return IntentResponse(
                intent="OPEN_URL",
                confidence=0.95,
                entities={"url": url}
            )

        for prefix in _URL_PREFIXES:
            if text.startswith(prefix):
                tail = text[len(prefix):].strip()
                if tail:
                    return IntentResponse(
                        intent="OPEN_URL",
                        confidence=0.95,
                        entities={"url": tail}
                    )

        # ==========================================
        # SEARCH YOUTUBE
        # Checked before OPEN/CLOSE to prevent
        # "search" being caught by those rules.
        # ==========================================

        if "search youtube" in text:

            query = text.replace("search youtube", "").strip()

            return IntentResponse(
                intent="SEARCH_YOUTUBE",
                confidence=0.95,
                entities={"query": query}
            )

        # ==========================================
        # OPEN APP
        # ==========================================

        if first in _OPEN_KEYWORDS:

            phrase = " ".join(
                w for w in words[1:]
                if w not in _FILLER_WORDS
            )

            app_name = normalize_app_name(phrase)

            if app_name:
                return IntentResponse(
                    intent="OPEN_APP",
                    confidence=0.9,
                    entities={"app_name": app_name}
                )

        # ==========================================
        # CLOSE APP
        # ==========================================

        if first in _CLOSE_KEYWORDS:

            phrase = " ".join(
                w for w in words[1:]
                if w not in _FILLER_WORDS
            )

            if phrase in _CONTEXTUAL_REFS:

                # Contextual resolution — use last remembered entity
                entity = memory.get_last_entity()

                if entity and entity.get("type") == "app":
                    return IntentResponse(
                        intent="CLOSE_APP",
                        confidence=0.90,
                        entities={"app_name": entity["value"]}
                    )

            else:

                app_name = normalize_app_name(phrase)

                if app_name:
                    return IntentResponse(
                        intent="CLOSE_APP",
                        confidence=0.9,
                        entities={"app_name": app_name}
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