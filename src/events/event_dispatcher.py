class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def register_listener(self, event_type, callback):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unregister_listener(self, event_type, callback):
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def dispatch_event(self, event_type, event_args):
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(event_args)

    def get_listeners(self, event_type):
        return self._listeners.get(event_type, [])