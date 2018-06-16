from rx.core import ObservableBase

from .pausable import PausableObservable
from .pausablebuffered import PausableBufferedObservable
from .controlledobservable import ControlledObservable

def pausable(source: ObservableBase, pauser) -> PausableObservable:
    """Pauses the underlying observable sequence based upon the observable
    sequence which yields True/False.

    Example:
    pauser = rx.Subject()
    source = rx.Observable.interval(100).pausable(pauser)

    Keyword parameters:
    pauser -- {Observable} The observable sequence used to pause the
        underlying sequence.

    Returns the observable {Observable} sequence which is paused based upon
    the pauser.
    """

    return PausableObservable(source, pauser)

def pausable_buffered(source: ObservableBase, subject) -> PausableBufferedObservable:
    """Pauses the underlying observable sequence based upon the observable
    sequence which yields True/False, and yields the values that were
    buffered while paused.

    Example:
    pauser = rx.Subject()
    source = rx.Observable.interval(100).pausable_buffered(pauser)

    Keyword arguments:
    pauser -- {Observable} The observable sequence used to pause the
        underlying sequence.

    Returns the observable {Observable} sequence which is paused based upon
    the pauser."""

    return PausableBufferedObservable(source, subject)

def controlled(self, enable_queue: bool = True, scheduler=None) -> ControlledObservable:
    """Attach a controller to the observable sequence

    Attach a controller to the observable sequence with the ability to
    queue.

    Example:
    source = rx.Observable.interval(100).controlled()
    source.request(3) # Reads 3 values

    Keyword arguments:
    enable_queue -- truthy value to determine if values should
        be queued pending the next request
    scheduler -- determines how the requests will be scheduled
    Returns the observable sequence which only propagates values on request.
    """

    return ControlledObservable(self, enable_queue, scheduler)
