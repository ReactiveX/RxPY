from typing import Callable, Optional
from rx.core import Observable, typing


def _to_set() -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            s = set()

            def on_completed():
                observer.on_next(s)
                observer.on_completed()

            return source.subscribe(
                s.add,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return to_set
