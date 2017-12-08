from rx.core import Observable

from rx.internal.iterable import Iterable


def while_do(condition, source):
    """Repeats source as long as condition holds emulating a while loop.

    Keyword arguments:
    condition -- The condition which determines if the source will be
        repeated.
    source -- The observable sequence that will be run if the condition
        function returns true.

    Returns an observable sequence which is repeated as long as the
        condition holds.
    """

    source = Observable.from_future(source)
    from .concat import concat
    sources = list(Iterable.while_do(condition, source))
    return concat(*sources)
