from typing import TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

_T = TypeVar("_T")


@curry_flip
def all_(source: Observable[_T], predicate: Predicate[_T]) -> Observable[bool]:
    """Determines whether all elements of an observable sequence satisfy a condition.

    Examples:
        >>> result = source.pipe(all(lambda x: x > 0))
        >>> result = all(lambda x: x > 0)(source)

    Args:
        source: The source observable sequence.
        predicate: A function to test each element for a condition.

    Returns:
        An observable sequence containing a single element determining
        whether all elements in the source sequence pass the test.
    """

    def filter_fn(v: _T):
        return not predicate(v)

    def mapping(b: bool) -> bool:
        return not b

    return source.pipe(
        ops.filter(filter_fn),
        ops.some(),
        ops.map(mapping),
    )


__all__ = ["all_"]
