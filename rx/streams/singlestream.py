from typing import Any

from rx.core import Disposable
from rx.core.typing import Observable, Observer, Scheduler
from rx.core.anonymousobserver import NoopObserver
from rx.disposables import SingleAssignmentDisposable


class SingleStream(Observer, Observable):
    """The SingleStream.

    A disposable observer that can be subscribed/chained with a single
    observer. It's subscription property may be assigned an upstream
    subscription that will be disposed together with the stream itself.
    """

    def __init__(self) -> None:
        self._observer = NoopObserver()  # type: Observer
        self._subscription = SingleAssignmentDisposable()

        super().__init__()

    def on_next(self, value: Any) -> None:
        self._observer.on_next(value)

    def on_error(self, error: Exception) -> None:
        try:
            self._observer.on_error(error)
        finally:
            self.dispose()

    def on_completed(self) -> None:
        try:
            self._observer.on_completed()
        finally:
            self.dispose()

    def subscribe(self, observer: Observer = None, scheduler: Scheduler = None) -> Disposable:
        self._observer = observer
        return Disposable.create(self.dispose)

    def chain(self, observer: Observer = None, scheduler: Scheduler = None) -> "SingleStream":
        self._observer = observer
        return self

    def set_subscription(self, value: Disposable):
        """Sets a subscription that will be disposed togeter with the
        stream."""
        self._subscription.disposable = value

    subscription = property(fset=set_subscription, doc="Sets the subscription.")

    def dispose(self) -> None:
        self._observer = NoopObserver()
        self._subscription.dispose()
