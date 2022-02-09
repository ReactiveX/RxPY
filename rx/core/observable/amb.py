from typing import TypeVar

from rx import never
from rx import operators as _
from rx.core import Observable

_T = TypeVar("_T")


def amb_(*sources: Observable[_T]) -> Observable[_T]:
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever reacted first.
    """

    acc: Observable[_T] = never()

    def func(previous: Observable[_T], current: Observable[_T]):
        return _.amb(previous)(current)

    for source in sources:
        acc = func(acc, source)

    return acc


__all__ = ["amb_"]
