from rx import never

from rx import operators as _
from rx.core import Observable


def _amb(*sources: Observable) -> Observable:
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever reacted first.
    """

    acc = never()

    def func(previous, current):
        return _.amb(previous)(current)

    for source in sources:
        acc = func(acc, source)

    return acc
