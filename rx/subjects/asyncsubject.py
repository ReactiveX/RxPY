import threading
from typing import Any

from rx.disposable import Disposable
from rx.core import Observable
from rx.core.typing import Observer
from rx.internal import DisposedException

from .innersubscription import InnerSubscription


class AsyncSubject(Observable, Observer):
    """Represents the result of an asynchronous operation. The last value
    before the close notification, or the error received through
    on_error, is sent to all subscribed observers."""

    def __init__(self) -> None:
        """Creates a subject that can only receive one value and that value is
        cached for all future observations."""

        super(AsyncSubject, self).__init__()

        self.is_disposed = False
        self.is_stopped = False
        self.value = None
        self.has_value = False
        self.observers = []
        self.exception = None

        self.lock = threading.RLock()

    def check_disposed(self) -> None:
        if self.is_disposed:
            raise DisposedException()

    def _subscribe_core(self, observer, scheduler=None):
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.observers.append(observer)
                return InnerSubscription(self, observer)

            ex = self.exception
            hv = self.has_value
            v = self.value

        if ex:
            observer.on_error(ex)
        elif hv:
            observer.on_next(v)
            observer.on_completed()
        else:
            observer.on_completed()

        return Disposable()

    def on_completed(self) -> None:
        value = None
        os = None
        hv = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []

                self.is_stopped = True
                value = self.value
                hv = self.has_value

        if os:
            if hv:
                for o in os:
                    o.on_next(value)
                    o.on_completed()
            else:
                for o in os:
                    o.on_completed()

    def on_error(self, error: Exception) -> None:
        os = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                self.exception = error

        if os:
            for o in os:
                o.on_error(error)

    def on_next(self, value: Any) -> None:
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.value = value
                self.has_value = True

    def dispose(self) -> None:
        with self.lock:
            self.is_disposed = True
            self.observers = None
            self.exception = None
            self.value = None
