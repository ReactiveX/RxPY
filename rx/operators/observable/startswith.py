from typing import Any
from rx.core import Observable, ObservableBase
from .concat import concat


def start_with(source: ObservableBase, *args: Any) -> ObservableBase:
    """Prepends a sequence of values to an observable sequence.

    1 - source.start_with(1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    start = Observable.from_iterable(args)
    sequence = [start, source]
    return concat(*sequence)
