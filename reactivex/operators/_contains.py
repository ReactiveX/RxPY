from typing import TypeVar

from reactivex import Observable, typing
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.internal.basic import default_comparer

_T = TypeVar("_T")


@curry_flip
def contains_(
    source: Observable[_T],
    value: _T,
    comparer: typing.Comparer[_T] | None = None,
) -> Observable[bool]:
    """Determines whether an observable sequence contains a specified element.

    Examples:
        >>> result = source.pipe(contains(42))
        >>> result = contains(42)(source)
        >>> result = source.pipe(contains(42, custom_comparer))

    Args:
        source: The source observable sequence.
        value: The value to locate in the source sequence.
        comparer: Optional equality comparer to compare elements.

    Returns:
        An observable sequence containing a single element determining
        whether the source sequence contains the specified value.
    """
    comparer_ = comparer or default_comparer

    def predicate(v: _T) -> bool:
        return comparer_(v, value)

    return source.pipe(
        ops.filter(predicate),
        ops.some(),
    )


__all__ = ["contains_"]
