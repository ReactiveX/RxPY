from typing import Callable, Optional

from rx.disposable import Disposable
from rx.core import ConnectableObservable, Observable, typing


def _ref_count() -> Callable[[ConnectableObservable], Observable]:
    """Returns an observable sequence that stays connected to the
    source as long as there is at least one subscription to the
    observable sequence.
    """

    connectable_subscription = [None]
    count = [0]

    def ref_count(source: ConnectableObservable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            count[0] += 1
            should_connect = count[0] == 1
            subscription = source.subscribe_observer(observer, scheduler=scheduler)
            if should_connect:
                connectable_subscription[0] = source.connect(scheduler)

            def dispose():
                subscription.dispose()
                count[0] -= 1
                if not count[0]:
                    connectable_subscription[0].dispose()

            return Disposable(dispose)

        return Observable(subscribe_observer=subscribe_observer)

    return ref_count
