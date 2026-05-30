# riya_engine/state/runtime_state.py

class RuntimeState:

    def __init__(self):

        self.active_tasks = {}

        self.completed_tasks = []

        self.failed_tasks = []

    # -----------------------------------
    # ACTIVE TASKS
    # -----------------------------------

    def add_active_task(self, task):

        self.active_tasks[
            task["task_id"]
        ] = task

    def remove_active_task(self, task_id):

        if task_id in self.active_tasks:

            del self.active_tasks[task_id]

    # -----------------------------------
    # COMPLETED TASKS
    # -----------------------------------

    def add_completed_task(self, task):

        self.completed_tasks.append(task)

    # -----------------------------------
    # FAILED TASKS
    # -----------------------------------

    def add_failed_task(self, task):

        self.failed_tasks.append(task)


runtime_state = RuntimeState()