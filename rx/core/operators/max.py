from typing import Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Comparer
from rx.internal.basic import identity

from .min import first_only

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
    return pipe(
        ops.max_by(identity, comparer),
        ops.map(first_only),
    )


__all__ = ["max_"]
