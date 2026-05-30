# runtime/event_bus.py
# Event bus for publish/subscribe communication in the Riya runtime
# riya_engine/runtime/event_bus.py

from collections import defaultdict


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_name, callback):
        self.listeners[event_name].append(callback)

    def emit(self, event_name, data=None):

        print(f"[EVENT EMITTED] {event_name}")

        for callback in self.listeners[event_name]:

            try:
                callback(data)

            except Exception as e:
                # Subscriber errors must never crash the emitter caller.
                # Log and continue so other subscribers still run.
                print(
                    f"[EVENT BUS ERROR] Subscriber '{callback.__name__}' "
                    f"raised on event '{event_name}': {e}"
                )

    def unsubscribe(self, event_name, callback):

        if callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)


# global singleton
event_bus = EventBus()