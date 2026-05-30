# runtime/execution_context.py
# Execution context management for the Riya runtime
# riya_engine/runtime/execution_context.py

import uuid
from datetime import datetime


class ExecutionContext:

    def __init__(self, user_input):

        self.request_id = str(uuid.uuid4())

        self.session_id = None

        self.user_input = user_input

        self.intent = None

        self.plan = None

        self.tasks = []

        self.execution_history = []

        self.created_at = datetime.utcnow()

    def add_history(self, event, data=None):

        self.execution_history.append({
            "event": event,
            "data": data
        })

    def set_intent(self, intent):
        self.intent = intent

    def set_plan(self, plan):
        self.plan = plan