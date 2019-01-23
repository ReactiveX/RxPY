from rx import never

from rx import operators as _
from rx.core import Observable, AnonymousObservable
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future


def _amb(*args: Observable) -> Observable:
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever reacted first.
    """

    acc = never()
    if isinstance(args[0], list):
        items = args[0]
    else:
        items = list(args)

    def func(previous, current):
        return _.amb(previous)(current)

    for item in items:
        acc = func(acc, item)

    return acc
