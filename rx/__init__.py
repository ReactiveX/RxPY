from typing import Iterable
from .core import Observer, Observable



def empty() -> Observable:
    """Returns an empty observable sequence.

    Example:
        >>> obs = empty()

    Args:
        scheduler -- Scheduler to send the termination call on.

    Returns:
        An observable sequence with no elements.
    """
    from .core.observable.empty import empty as empty_
    return empty_()

def from_iterable(iterable: Iterable) -> Observable:
    """Converts an iterable to an observable sequence.

    Example:
        >>> from_iterable([1,2,3])

    Args:
        iterable - A Python iterable

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """
    from .core.observable.fromiterable import from_iterable as from_iterable_
    return from_iterable_(iterable)

from_ = from_iterable
from_list = from_iterable

def throw(exception: Exception) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError
    message.

    Example:
        >>> res = rx.Observable.throw(Exception('Error'))

    Args:
        exception -- An object used for the sequence's termination.

    Returns:
        The observable sequence that terminates exceptionally with the
        specified exception object.
    """
    from .core.observable.throw import throw as throw_
    return throw_(exception)