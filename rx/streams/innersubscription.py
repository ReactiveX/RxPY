from rx import Lock


class InnerSubscription(object):
    def __init__(self, stream, observer):
        self.stream = stream
        self.observer = observer

        self.lock = Lock()

    def dispose(self):
        with self.lock:
            if not self.stream.is_disposed and self.observer:
                if self.observer in self.stream.observers:
                    self.stream.observers.remove(self.observer)
                self.observer = None
