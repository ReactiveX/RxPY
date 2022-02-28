import threading
from typing import List, Optional, TypeVar

from .. import abc
from ..disposable import Disposable
from ..internal import DisposedException
from ..observable import Observable
from ..observer import Observer
from .innersubscription import InnerSubscription

_T = TypeVar("_T")


class Subject(Observable[_T], Observer[_T], abc.SubjectBase[_T]):
    """Represents an object that is both an observable sequence as well
    as an observer. Each notification is broadcasted to all subscribed
    observers.
    """

    def __init__(self) -> None:
        super().__init__()

        self.is_disposed = False
        self.observers: List[abc.ObserverBase[_T]] = []
        self.exception: Optional[Exception] = None

        self.lock = threading.RLock()

    def check_disposed(self) -> None:
        if self.is_disposed:
            raise DisposedException()

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

            if self.exception is not None:
                observer.on_error(self.exception)
            else:
                observer.on_completed()
            return Disposable()

    def on_next(self, value: _T) -> None:
        """Notifies all subscribed observers with the value.

        Args:
            value: The value to send to all subscribed observers.
        """

        with self.lock:
            self.check_disposed()
        super().on_next(value)

    def _on_next_core(self, value: _T) -> None:
        with self.lock:
            observers = self.observers.copy()

        for observer in observers:
            observer.on_next(value)

    def on_error(self, error: Exception) -> None:
        """Notifies all subscribed observers with the exception.

        Args:
            error: The exception to send to all subscribed observers.
        """

        with self.lock:
            self.check_disposed()
        super().on_error(error)

    def _on_error_core(self, error: Exception) -> None:
        with self.lock:
            observers = self.observers.copy()
            self.observers.clear()
            self.exception = error

        for observer in observers:
            observer.on_error(error)

    def on_completed(self) -> None:
        """Notifies all subscribed observers of the end of the sequence."""

        with self.lock:
            self.check_disposed()
        super().on_completed()

    def _on_completed_core(self) -> None:
        with self.lock:
            observers = self.observers.copy()
            self.observers.clear()

        for observer in observers:
            observer.on_completed()

    def dispose(self) -> None:
        """Unsubscribe all observers and release resources."""

        with self.lock:
            self.is_disposed = True
            self.observers = []
            self.exception = None
            super().dispose()
