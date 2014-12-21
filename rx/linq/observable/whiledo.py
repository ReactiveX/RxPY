from rx.observable import Observable

from rx.internal.enumerable import Enumerable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def while_do(cls, condition, source):
    """Repeats source as long as condition holds emulating a while loop.

    Keyword arguments:
    condition -- {Function} The condition which determines if the source
        will be repeated.
    source -- {Observable} The observable sequence that will be run if the
        condition function returns true.

    Returns an observable {Observable} sequence which is repeated as long
    as the condition holds.
    """

    source = Observable.from_future(source)
    return Observable.concat(Enumerable.while_do(condition, source))
