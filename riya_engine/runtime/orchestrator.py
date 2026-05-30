# riya_engine/runtime/orchestrator.py

from riya_engine.runtime.task_manager import task_manager

from riya_engine.capabilities.registry import CAPABILITY_REGISTRY

from riya_engine.runtime.logger import logger

from riya_engine.runtime.events import Events


def execute_capability(capability_name, payload):
    """Look up and call a capability from the registry."""

    capability_function = CAPABILITY_REGISTRY.get(capability_name)

    if not capability_function:
        raise RuntimeError(f"Capability not found: {capability_name}")

    return capability_function(payload)


class Orchestrator:

    def execute_task(self, task):
        capability_name = task["capability"]
        payload = task["payload"]

        task_manager.start_task(task)

        try:
            response = execute_capability(capability_name, payload)

            # Defensive guard
            if response is None:
                task_manager.fail_task(
                    task,
                    f"Capability '{capability_name}' returned None"
                )
                return False

            # Capability failure
            if not response.success:
                task_manager.fail_task(task, response.error)
                return False

            # Success — store result then complete
            task["result"] = response.to_dict()
            task_manager.complete_task(task)
            return True

        except Exception as e:
            task_manager.fail_task(task, str(e))
            return False


orchestrator = Orchestrator()