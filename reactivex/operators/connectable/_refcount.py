from typing import Callable, Optional, TypeVar

from reactivex import ConnectableObservable, Observable, abc
from reactivex.disposable import Disposable

_T = TypeVar("_T")


def ref_count_() -> Callable[[ConnectableObservable[_T]], Observable[_T]]:
    """Returns an observable sequence that stays connected to the
    source as long as there is at least one subscription to the
    observable sequence.
    """

    connectable_subscription: Optional[abc.DisposableBase] = None
    count = 0

    def ref_count(source: ConnectableObservable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            nonlocal connectable_subscription, count

            count += 1
            should_connect = count == 1
            subscription = source.subscribe(observer, scheduler=scheduler)
            if should_connect:
                connectable_subscription = source.connect(scheduler)

            def dispose() -> None:
                nonlocal connectable_subscription, count

                subscription.dispose()
                count -= 1
                if not count and connectable_subscription:
                    connectable_subscription.dispose()

            return Disposable(dispose)

        return Observable(subscribe)

    return ref_count


__all__ = ["ref_count_"]
