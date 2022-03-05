import threading
from typing import TYPE_CHECKING, Optional, TypeVar

from .. import abc

if TYPE_CHECKING:
    from .subject import Subject

_T = TypeVar("_T")


class InnerSubscription(abc.DisposableBase):
    def __init__(
        self, subject: "Subject[_T]", observer: Optional[abc.ObserverBase[_T]] = None
    ):
        self.subject = subject
        self.observer = observer

        self.lock = threading.RLock()

    def dispose(self) -> None:
        with self.lock:
            if not self.subject.is_disposed and self.observer:
                if self.observer in self.subject.observers:
                    self.subject.observers.remove(self.observer)
                self.observer = None
