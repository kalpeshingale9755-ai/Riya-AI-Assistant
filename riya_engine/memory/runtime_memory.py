# riya_engine/memory/runtime_memory.py

class RuntimeMemory:

    def __init__(self):

        self.execution_history = []

        self.completed_tasks = []

    def remember(self, event_type, data):

        memory_entry = {
            "event": event_type,
            "data": data
        }

        self.execution_history.append(
            memory_entry
        )

    def add_task(self, task):
        """Persist a completed task record. Called by MemoryOrchestrator.store_task()."""

        self.completed_tasks.append(task)

    def get_history(self):

        return self.execution_history

    def get_completed_tasks(self):

        return self.completed_tasks


runtime_memory = RuntimeMemory()