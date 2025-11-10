from typing import TypeVar, cast

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

from ._firstordefault import first_or_default_async_

_T = TypeVar("_T")


@curry_flip
def first_(
    source: Observable[_T],
    predicate: Predicate[_T] | None = None,
) -> Observable[_T]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    Examples:
        >>> res = source.pipe(first())
        >>> res = first()(source)
        >>> res = source.pipe(first(lambda x: x > 3))

    Args:
        source: The source observable sequence.
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate if
        provided, else the first item in the sequence.
    """

    if predicate:
        return source.pipe(ops.filter(predicate), ops.first())

    # first_or_default_async_(False) returns
    # Callable[[Observable[_T]], Observable[_T]] but the type checker
    # cannot infer it. This cast is safe - implementation preserves type.
    return cast(Observable[_T], first_or_default_async_(False)(source))


__all__ = ["first_"]
