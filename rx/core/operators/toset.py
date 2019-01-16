from typing import Callable
from rx.core import Observable, AnonymousObservable


def _to_set() -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            s = set()

            def on_completed():
                observer.on_next(s)
                observer.on_completed()

            return source.subscribe_(s.add, observer.on_error, on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return to_set