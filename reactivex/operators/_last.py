from typing import TypeVar

from reactivex import Observable, operators
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

from ._lastordefault import last_or_default_async

_T = TypeVar("_T")


@curry_flip
def last_(
    source: Observable[_T],
    predicate: Predicate[_T] | None = None,
) -> Observable[_T]:
    """Returns the last element of an observable sequence that
    satisfies the condition in the predicate if specified, else
    the last element.

    Examples:
        >>> res = source.pipe(last())
        >>> res = last()(source)
        >>> res = source.pipe(last(lambda x: x > 3))

    Args:
        source: Source observable to get last item from.
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the last element in the
        observable sequence that satisfies the condition in the
        predicate.
    """
    from typing import cast

    if predicate:
        return source.pipe(
            operators.filter(predicate),
            operators.last(),
        )

    # last_or_default_async returns Observable[_T | None], but when has_default=False
    # it will never emit None (either emits _T or errors). Safe to cast to Observable[_T].
    return cast(Observable[_T], last_or_default_async(source, False))


__all__ = ["last_"]
