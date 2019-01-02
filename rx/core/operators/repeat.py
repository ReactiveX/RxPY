from typing import Any
from rx.core import ObservableBase, Observable


def repeat_value(value: Any = None, repeat_count: int = None) -> ObservableBase:
    """Generates an observable sequence that repeats the given element
    the specified number of times.

    1 - res = repeat_value(42)
    2 - res = repeat_value(42, 4)

    Keyword arguments:
    value -- Element to repeat.
    repeat_count -- [Optional] Number of times to repeat the element.
        If not specified, repeats indefinitely.

    Returns an observable sequence that repeats the given element the
    specified number of times."""

    if repeat_count == -1:
        repeat_count = None

    xs = Observable.return_value(value)
    return xs.repeat(repeat_count)
