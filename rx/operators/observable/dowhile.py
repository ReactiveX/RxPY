from rx.core import Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def do_while(source, condition):
    """Repeats source as long as condition holds emulating a do while loop.

    Keyword arguments:
    condition -- {Function} The condition which determines if the source
        will be repeated.

    Returns an observable {Observable} sequence which is repeated as long
    as the condition holds.
    """

    return source.concat(Observable.while_do(condition, source))