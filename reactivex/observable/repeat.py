from typing import Optional, TypeVar

import reactivex
from reactivex import Observable
from reactivex import operators as ops

_T = TypeVar("_T")


def repeat_value_(value: _T, repeat_count: Optional[int] = None) -> Observable[_T]:
    """Generates an observable sequence that repeats the given element
    the specified number of times.

    Examples:
        1 - res = repeat_value(42)
        2 - res = repeat_value(42, 4)

    Args:
        value: Element to repeat.
        repeat_count: [Optional] Number of times to repeat the element.
            If not specified, repeats indefinitely.

    Returns:
        An observable sequence that repeats the given element the
        specified number of times.
    """

    if repeat_count == -1:
        repeat_count = None

    xs = reactivex.return_value(value)
    return xs.pipe(ops.repeat(repeat_count))


__all__ = ["repeat_value_"]
