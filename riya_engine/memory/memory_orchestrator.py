# riya_engine/memory/memory_orchestrator.py

from riya_engine.memory.context_memory import context_memory

from riya_engine.memory.runtime_memory import runtime_memory

from riya_engine.runtime.event_bus import event_bus

from riya_engine.runtime.event_types import MEMORY_UPDATED


class MemoryOrchestrator:

    # ==========================================
    # STORE ENTITY
    # ==========================================

    def store_entity(self, entity):

        context_memory.set_last_entity(entity)

        self._emit_update(
            "ENTITY_STORED",
            entity
        )

    # ==========================================
    # STORE ACTION
    # ==========================================

    def store_action(self, action):

        context_memory.set_last_action(action)

        self._emit_update(
            "ACTION_STORED",
            {
                "action": action
            }
        )

    # ==========================================
    # STORE TASK
    # ==========================================

    def store_task(self, task):

        runtime_memory.add_task(task)

        self._emit_update(
            "TASK_STORED",
            task
        )

    # ==========================================
    # GET LAST ENTITY
    # ==========================================

    def get_last_entity(self):

        return context_memory.get_last_entity()

    # ==========================================
    # GET LAST ACTION
    # ==========================================

    def get_last_action(self):

        return context_memory.get_last_action()

    # ==========================================
    # INTERNAL MEMORY EVENT
    # ==========================================

    def _emit_update(self, update_type, data):

        event_bus.emit(
            MEMORY_UPDATED,
            {
                "update_type": update_type,
                "data": data
            }
        )


memory = MemoryOrchestrator()