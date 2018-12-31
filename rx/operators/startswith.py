from typing import Any
from rx.core import Observable, StaticObservable
from .concat import concat


def start_with(source: Observable, *args: Any) -> Observable:
    """Prepends a sequence of values to an observable sequence.

    1 - source.start_with(1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    start = StaticObservable.from_iterable(args)
    sequence = [start, source]
    return concat(*sequence)
