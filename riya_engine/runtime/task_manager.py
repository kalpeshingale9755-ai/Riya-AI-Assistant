# runtime/task_manager.py
# Task management and scheduling for the Riya runtime
# riya_engine/runtime/task_manager.py

import uuid

from riya_engine.runtime.lifecycle import TaskState
from riya_engine.runtime.logger import logger
from riya_engine.runtime.events import Events
from riya_engine.runtime.event_bus import event_bus


class TaskManager:

    def create_task(self, capability_name, payload):

        task = {
            "task_id": str(uuid.uuid4()),
            "capability": capability_name,
            "payload": payload,
            "state": TaskState.PENDING
        }

        logger.log(
            Events.TASK_CREATED,
            task
        )

        event_bus.emit(
            Events.TASK_CREATED,
            task
        )

        return task

    def start_task(self, task):

        task["state"] = TaskState.RUNNING

        logger.log(
            Events.TASK_STARTED,
            task
        )

        event_bus.emit(
            Events.TASK_STARTED,
            task
        )

    def complete_task(self, task):

        task["state"] = TaskState.SUCCESS

        logger.log(
            Events.TASK_COMPLETED,
            task
        )

        event_bus.emit(
            Events.TASK_COMPLETED,
            task
        )

    def fail_task(self, task, error):

        task["state"] = TaskState.FAILED

        task["error"] = error

        logger.log(
            Events.TASK_FAILED,
            task
        )

        event_bus.emit(
            Events.TASK_FAILED,
            task
        )


task_manager = TaskManager()