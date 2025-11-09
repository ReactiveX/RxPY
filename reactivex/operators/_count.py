from typing import TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

_T = TypeVar("_T")


@curry_flip
def count_(
    source: Observable[_T],
    predicate: Predicate[_T] | None = None,
) -> Observable[int]:
    """Returns an observable sequence containing a single element with the
    number of elements in the source sequence.

    Examples:
        >>> result = source.pipe(count())
        >>> result = count()(source)
        >>> result = source.pipe(count(lambda x: x > 5))

    Args:
        source: The source observable.
        predicate: Optional predicate to filter elements before counting.

    Returns:
        An observable sequence containing a single element with the count.
    """
    if predicate:
        return source.pipe(
            ops.filter(predicate),
            ops.count(),
        )

    def reducer(n: int, _: _T) -> int:
        return n + 1

    return source.pipe(ops.reduce(reducer, seed=0))


__all__ = ["count_"]
