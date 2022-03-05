from typing import Optional, TypeVar, cast

from .. import abc
from ..disposable import Disposable
from .innersubscription import InnerSubscription
from .subject import Subject

_T = TypeVar("_T")


class AsyncSubject(Subject[_T]):
    """Represents the result of an asynchronous operation. The last value
    before the close notification, or the error received through
    on_error, is sent to all subscribed observers."""

    def __init__(self) -> None:
        """Creates a subject that can only receive one value and that value is
        cached for all future observations."""

        super().__init__()

        self.value: _T = cast(_T, None)
        self.has_value: bool = False

    def _subscribe_core(
        self,
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.observers.append(observer)
                return InnerSubscription(self, observer)

            ex = self.exception
            has_value = self.has_value
            value = self.value

        if ex:
            observer.on_error(ex)
        elif has_value:
            observer.on_next(value)
            observer.on_completed()
        else:
            observer.on_completed()

        return Disposable()

    def _on_next_core(self, value: _T) -> None:
        """Remember the value. Upon completion, the most recently received value
        will be passed on to all subscribed observers.

        Args:
            value: The value to remember until completion
        """
        with self.lock:
            self.value = value
            self.has_value = True

    def _on_completed_core(self) -> None:
        """Notifies all subscribed observers of the end of the sequence. The
        most recently received value, if any, will now be passed on to all
        subscribed observers."""

        with self.lock:
            observers = self.observers.copy()
            self.observers.clear()
            value = self.value
            has_value = self.has_value

        if has_value:
            for observer in observers:
                observer.on_next(value)
                observer.on_completed()
        else:
            for observer in observers:
                observer.on_completed()

    def dispose(self) -> None:
        """Unsubscribe all observers and release resources."""

        with self.lock:
            self.value = cast(_T, None)
            super().dispose()
