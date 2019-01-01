from typing import Any, Callable
from rx.core import Observable, StaticObservable
from .concat import concat


def start_with(*args: Any) -> Callable[[Observable], Observable]:
    """Prepends a sequence of values to an observable sequence.

    1 - source.start_with(1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    def partial(source: Observable) -> Observable:
        start = StaticObservable.from_iterable(args)
        sequence = [start, source]
        return concat(*sequence)
    return partial
