# riya_engine/runtime/debug_subscriber.py

from riya_engine.runtime.event_bus import event_bus

from riya_engine.runtime.event_types import *


def debug_listener(data):

    print("\n[EVENT TRACE]")

    print(data)


# ==========================================
# SUBSCRIBE TO ALL EVENTS
# ==========================================

event_bus.subscribe(
    INPUT_RECEIVED,
    debug_listener
)

event_bus.subscribe(
    TEXT_CLEANED,
    debug_listener
)

event_bus.subscribe(
    COMMAND_SPLIT,
    debug_listener
)

event_bus.subscribe(
    ENTITY_NORMALIZED,
    debug_listener
)

event_bus.subscribe(
    INTENT_DETECTED,
    debug_listener
)

event_bus.subscribe(
    PLAN_CREATED,
    debug_listener
)

event_bus.subscribe(
    MEMORY_UPDATED,
    debug_listener
)

event_bus.subscribe(
    TASK_CREATED,
    debug_listener
)

event_bus.subscribe(
    TASK_STARTED,
    debug_listener
)

event_bus.subscribe(
    TASK_COMPLETED,
    debug_listener
)

event_bus.subscribe(
    TASK_FAILED,
    debug_listener
)