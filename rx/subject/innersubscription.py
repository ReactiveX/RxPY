import threading
from typing import TypeVar

from rx.core import abc
from rx.core.abc.observable import ObservableBase

_T = TypeVar("_T")


class InnerSubscription(abc.DisposableBase):
    def __init__(self, subject: abc.SubjectBase[_T], observer: ObservableBase[_T]):
        self.subject = subject
        self.observer = observer

        self.lock = threading.RLock()

    def dispose(self) -> None:
        with self.lock:
            if not self.subject.is_disposed and self.observer:
                if self.observer in self.subject.observers:
                    self.subject.observers.remove(self.observer)
                self.observer = None
