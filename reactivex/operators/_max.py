from collections.abc import Callable
from typing import TypeVar, cast

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.internal.basic import identity
from reactivex.typing import Comparer

from ._min import first_only

_T = TypeVar("_T")


@curry_flip
def max_(
    source: Observable[_T],
    comparer: Comparer[_T] | None = None,
) -> Observable[_T]:
    """Returns the maximum value in an observable sequence.

    Returns the maximum value in an observable sequence according to
    the specified comparer.

    Examples:
        >>> result = source.pipe(max())
        >>> result = max()(source)
        >>> result = source.pipe(max(lambda x, y: x.value - y.value))

    Args:
        source: The source observable.
        comparer: Optional comparer used to compare elements.

    Returns:
        An observable sequence containing a single element with the
        maximum element in the source sequence.
    """
    return source.pipe(
        ops.max_by(cast(Callable[[_T], _T], identity), comparer),
        ops.map(first_only),
    )


__all__ = ["max_"]
