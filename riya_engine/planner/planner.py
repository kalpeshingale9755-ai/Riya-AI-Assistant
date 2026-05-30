# riya_engine/planner/planner.py

class Planner:

    def create_plan(self, intent_response):

        intent = intent_response.intent

        entities = intent_response.entities

        # ==========================================
        # OPEN APP
        # ==========================================

        if intent == "OPEN_APP":

            return [
                {
                    "step": 1,
                    "capability": "open_app",
                    "payload": {
                        "app_name": entities["app_name"]
                    }
                }
            ]

        # ==========================================
        # CLOSE APP
        # ==========================================

        if intent == "CLOSE_APP":

            return [
                {
                    "step": 1,
                    "capability": "close_app",
                    "payload": {
                        "app_name": entities["app_name"]
                    }
                }
            ]

        # ==========================================
        # SEARCH YOUTUBE WORKFLOW
        # ==========================================

        if intent == "SEARCH_YOUTUBE":

            query = entities.get("query")

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