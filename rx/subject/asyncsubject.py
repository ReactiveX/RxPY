from typing import Any, Optional

from rx.disposable import Disposable
from rx.core import typing

from .subject import Subject
from .innersubscription import InnerSubscription


class AsyncSubject(Subject):
    """Represents the result of an asynchronous operation. The last value
    before the close notification, or the error received through
    on_error, is sent to all subscribed observers."""

    def __init__(self) -> None:
        """Creates a subject that can only receive one value and that value is
        cached for all future observations."""

        super().__init__()

        self.value = None
        self.has_value = False

    def _subscribe_core(self,
                        observer: typing.Observer,
                        scheduler: Optional[typing.Scheduler] = None
                        ) -> typing.Disposable:
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

    def on_next(self, value: Any) -> None:
        """Remember the value. Upon completion, the most recently received value
        will be passed on to all subscribed observers.

        Args:
            value: The value to remember until completion
        """
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.value = value
                self.has_value = True

    def on_completed(self) -> None:
        """Notifies all subscribed observers of the end of the sequence. The
        most recently received value, if any, will now be passed on to all
        subscribed observers."""

        value = None
        has_value = None
        observers = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                observers = self.observers[:]
                self.observers = []
                self.is_stopped = True
                value = self.value
                has_value = self.has_value

        if observers:
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
            self.value = None
            super().dispose()
