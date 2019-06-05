import threading

from rx.core import typing


class InnerSubscription(typing.Disposable):
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer

        self.lock = threading.RLock()

    def dispose(self) -> None:
        with self.lock:
            if not self.subject.is_disposed and self.observer:
                if self.observer in self.subject.observers:
                    self.subject.observers.remove(self.observer)
                self.observer = None
