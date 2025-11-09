from typing import TypeVar, cast

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

from ._singleordefault import single_or_default_async_

_T = TypeVar("_T")


@curry_flip
def single_(
    source: Observable[_T],
    predicate: Predicate[_T] | None = None,
) -> Observable[_T]:
    """Returns the only element of an observable sequence that satisfies the
    condition in the optional predicate, and reports an exception if there
    is not exactly one element in the observable sequence.

    Examples:
        >>> res = source.pipe(single())
        >>> res = single()(source)
        >>> res = source.pipe(single(lambda x: x == 42))

    Args:
        source: The source observable sequence.
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate.
    """

    if predicate:
        return source.pipe(ops.filter(predicate), ops.single())
    else:
        # single_or_default_async_(False) returns a Callable[[Observable[_T]], Observable[_T]]
        # but the type checker cannot infer the generic type parameter.
        # This cast is safe because the implementation preserves the type parameter.
        return cast(Observable[_T], single_or_default_async_(False)(source))


__all__ = ["single_"]
