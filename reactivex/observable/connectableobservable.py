from typing import List, Optional, TypeVar

from reactivex import abc
from reactivex.disposable import CompositeDisposable, Disposable

from .observable import Observable

_T = TypeVar("_T")


class ConnectableObservable(Observable[_T]):
    """Represents an observable that can be connected and
    disconnected."""

    def __init__(self, source: abc.ObservableBase[_T], subject: abc.SubjectBase[_T]):
        self.subject = subject
        self.has_subscription = False
        self.subscription: Optional[abc.DisposableBase] = None
        self.source = source

        super().__init__()

    def _subscribe_core(
        self,
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        return self.subject.subscribe(observer, scheduler=scheduler)

    def connect(
        self, scheduler: Optional[abc.SchedulerBase] = None
    ) -> Optional[abc.DisposableBase]:
        """Connects the observable."""

        if not self.has_subscription:
            self.has_subscription = True

            def dispose() -> None:
                self.has_subscription = False

            subscription = self.source.subscribe(self.subject, scheduler=scheduler)
            self.subscription = CompositeDisposable(subscription, Disposable(dispose))

        return self.subscription

    def auto_connect(self, subscriber_count: int = 1) -> Observable[_T]:
        """Returns an observable sequence that stays connected to the
        source indefinitely to the observable sequence.
        Providing a subscriber_count will cause it to connect() after
        that many subscriptions occur. A subscriber_count of 0 will
        result in emissions firing immediately without waiting for
        subscribers.
        """

        connectable_subscription: List[Optional[abc.DisposableBase]] = [None]
        count = [0]
        source = self
        is_connected = [False]

        if subscriber_count == 0:
            connectable_subscription[0] = source.connect()
            is_connected[0] = True

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            count[0] += 1
            should_connect = count[0] == subscriber_count and not is_connected[0]
            subscription = source.subscribe(observer)
            if should_connect:
                connectable_subscription[0] = source.connect(scheduler)
                is_connected[0] = True

            def dispose() -> None:
                subscription.dispose()
                count[0] -= 1
                is_connected[0] = False

            return Disposable(dispose)

        return Observable(subscribe)
