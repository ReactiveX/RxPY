from typing import Any

from rx.disposable import Disposable

from .subject import Subject
from .innersubscription import InnerSubscription


class BehaviorSubject(Subject):
    """Represents a value that changes over time. Observers can
    subscribe to the subject to receive the last (or initial) value and
    all subsequent notifications.
    """

    def __init__(self, value) -> None:
        """Initializes a new instance of the BehaviorSubject class which
        creates a subject that caches its last value and starts with the
        specified value.

        Args:
            value: Initial value sent to observers when no other value has been
                received by the subject yet.
        """

        super().__init__()

        self.value = value

    def _subscribe_core(self, observer, scheduler=None):
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.observers.append(observer)
                observer.on_next(self.value)
                return InnerSubscription(self, observer)
            ex = self.exception

        if ex:
            observer.on_error(ex)
        else:
            observer.on_completed()

        return Disposable()

    def _on_next_core(self, value: Any) -> None:
        """Notifies all subscribed observers with the value."""
        with self.lock:
            observers = self.observers.copy()
            self.value = value

        for observer in observers:
            observer.on_next(value)

    def dispose(self) -> None:
        """Release all resources.

        Releases all resources used by the current instance of the
        BehaviorSubject class and unsubscribe all observers.
        """

        with self.lock:
            self.value = None
            super().dispose()
