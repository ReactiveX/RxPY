from typing import TypeVar

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def start_with_(source: Observable[_T], *args: _T) -> Observable[_T]:
    """Prepends a sequence of values to an observable sequence.

    Example:
        >>> result = source.pipe(start_with(1, 2, 3))
        >>> result = start_with(1, 2, 3)(source)

    Args:
        source: The source observable sequence.
        args: Values to prepend to the source sequence.

    Returns:
        The source sequence prepended with the specified values.
    """
    start = reactivex.from_iterable(args)
    sequence = [start, source]
    return reactivex.concat(*sequence)


__all__ = ["start_with_"]
