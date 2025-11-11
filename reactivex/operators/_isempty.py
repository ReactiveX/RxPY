from typing import TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def is_empty_(source: Observable[_T]) -> Observable[bool]:
    """Determines whether an observable sequence is empty.

    Examples:
        >>> res = source.pipe(is_empty())
        >>> res = is_empty()(source)

    Args:
        source: The source observable sequence.

    Returns:
        An observable sequence containing a single element
        determining whether the source sequence is empty.
    """

    def mapper(b: bool) -> bool:
        return not b

    return source.pipe(
        ops.some(),
        ops.map(mapper),
    )


__all__ = ["is_empty_"]
