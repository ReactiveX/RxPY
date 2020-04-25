from typing import Callable
from rx.core import Observable


def _to_set() -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            s = set()

            def on_completed():
                nonlocal s
                observer.on_next(s)
                s = set()
                observer.on_completed()

            return source.subscribe_(s.add, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return to_set