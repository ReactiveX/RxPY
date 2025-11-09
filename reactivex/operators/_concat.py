from typing import TypeVar

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def concat_(source: Observable[_T], *sources: Observable[_T]) -> Observable[_T]:
    """Concatenates all the observable sequences.

    Examples:
        >>> result = source.pipe(concat(xs, ys, zs))
        >>> result = concat(xs, ys, zs)(source)

    Args:
        source: The source observable sequence.
        sources: Additional observable sequences to concatenate.

    Returns:
        An observable sequence that contains the elements of
        each given sequence, in sequential order.
    """
    return reactivex.concat(source, *sources)


__all__ = ["concat_"]
