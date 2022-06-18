from typing import Callable, Optional, TypeVar, cast

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.internal.basic import identity
from reactivex.typing import Comparer

from ._min import first_only

_T = TypeVar("_T")


def max_(
    comparer: Optional[Comparer[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the maximum value in an observable sequence according to
    the specified comparer.

    Examples:
        >>> op = max()
        >>> op = max(lambda x, y:  x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        maximum element in the source sequence.
    """
    return compose(
        ops.max_by(cast(Callable[[_T], _T], identity), comparer),
        ops.map(first_only),
    )


__all__ = ["max_"]
