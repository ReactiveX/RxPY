from typing import Callable, Optional, TypeVar

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.typing import Predicate

from ._firstordefault import first_or_default_async_

_T = TypeVar("_T")


def first_(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    Examples:
        >>> res = res = first()(source)
        >>> res = res = first(lambda x: x > 3)(source)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate if
        provided, else the first item in the sequence.
    """

    if predicate:
        return compose(ops.filter(predicate), ops.first())

    return first_or_default_async_(False)


__all__ = ["first_"]
