from typing import Callable, List, Optional, TypeVar, cast

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.internal.basic import identity
from reactivex.internal.exceptions import SequenceContainsNoElementsError
from reactivex.typing import Comparer

_T = TypeVar("_T")


def first_only(x: List[_T]) -> _T:
    if not x:
        raise SequenceContainsNoElementsError()

    return x[0]


def min_(
    comparer: Optional[Comparer[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The `min` operator.

    Returns the minimum element in an observable sequence according to
    the optional comparer else a default greater than less than check.

    Examples:
        >>> res = source.min()
        >>> res = source.min(lambda x, y: x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An observable sequence containing a single element
        with the minimum element in the source sequence.
    """
    return compose(
        ops.min_by(cast(Callable[[_T], _T], identity), comparer),
        ops.map(first_only),
    )


__all__ = ["min_"]
