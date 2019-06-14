from typing import Optional

from rx.core import typing
from rx.disposable import Disposable
from rx.disposable import CompositeDisposable

from .observable import Observable


class ConnectableObservable(Observable):
    """Represents an observable that can be connected and
    disconnected."""

    def __init__(self, source, subject):
        self.subject = subject
        self.has_subscription = False
        self.subscription = None
        self.source = source

        super().__init__()

    def _subscribe_core(self, observer, scheduler=None):
        return observer.subscribe_to(self.subject, scheduler=scheduler)

    def connect(self, scheduler=None):
        """Connects the observable."""

        if not self.has_subscription:
            self.has_subscription = True

            def dispose():
                self.has_subscription = False

            disp = self.subject.subscribe_to(self.source, scheduler=scheduler)
            self.subscription = CompositeDisposable(disp, Disposable(dispose))

        return self.subscription

    def auto_connect(self, subscriber_count=1):
        """Returns an observable sequence that stays connected to the
        source indefinitely to the observable sequence.
        Providing a subscriber_count will cause it to connect() after
        that many subscriptions occur. A subscriber_count of 0 will
        result in emissions firing immediately without waiting for
        subscribers.
        """

        connectable_subscription = [None]
        count = [0]
        source = self
        is_connected = [False]

        if subscriber_count == 0:
            connectable_subscription[0] = source.connect()
            is_connected[0] = True

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            count[0] += 1
            should_connect = count[0] == subscriber_count and not is_connected[0]
            subscription = observer.subscribe_to(source)
            if should_connect:
                connectable_subscription[0] = source.connect(scheduler)
                is_connected[0] = True

            def dispose():
                subscription.dispose()
                count[0] -= 1
                is_connected[0] = False

            return Disposable(dispose)
        return Observable(subscribe_observer)
