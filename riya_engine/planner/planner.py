# riya_engine/planner/planner.py

class Planner:

    def create_plan(self, intent_response):

        intent = intent_response.intent

        entities = intent_response.entities

        # ==========================================
        # OPEN APP
        # ==========================================

        if intent == "OPEN_APP":

            app_name = entities.get("app_name")

            if not app_name:
                return []

            return [
                {
                    "step": 1,
                    "capability": "open_app",
                    "payload": {
                        "app_name": app_name
                    }
                }
            ]

        # ==========================================
        # CLOSE APP
        # ==========================================

        if intent == "CLOSE_APP":

            app_name = entities.get("app_name")

            if not app_name:
                return []

            return [
                {
                    "step": 1,
                    "capability": "close_app",
                    "payload": {
                        "app_name": app_name
                    }
                }
            ]

        # ==========================================
        # OPEN URL
        # ==========================================

        if intent == "OPEN_URL":

            url = entities.get("url")

            if not url:
                return []

            return [
                {
                    "step": 1,
                    "capability": "open_url",
                    "payload": {
                        "url": url
                    }
                }
            ]

        # ==========================================
        # SEARCH YOUTUBE WORKFLOW
        # ==========================================

        if intent == "SEARCH_YOUTUBE":

            query = entities.get("query")

            if not query:
                return []

            return [

                {
                    "step": 1,
                    "capability": "open_app",
                    "payload": {
                        "app_name": "chrome"
                    }
                },

                {
                    "step": 2,
                    "capability": "search_youtube",
                    "payload": {
                        "query": query
                    }
                }

            ]

        # ==========================================
        # UNKNOWN
        # ==========================================

        return []


planner = Planner()