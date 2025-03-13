from typing import Callable, Optional, TypeVar, cast

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.typing import Predicate

_T = TypeVar("_T")


def single_(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the only element of an observable sequence that satisfies the
    condition in the optional predicate, and reports an exception if there
    is not exactly one element in the observable sequence.

    Example:
        >>> res = single()
        >>> res = single(lambda x: x == 42)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate.
    """

    if predicate:
        return compose(ops.filter(predicate), ops.single())
    else:
        return cast(
            Callable[[Observable[_T]], Observable[_T]],
            ops.single_or_default_async(False),
        )


__all__ = ["single_"]
