from rx.concurrency import Scheduler
from rx.observable import Observable

from rx.concurrency import immediate_scheduler
from rx.internal import extensionmethod


@extensionmethod(Observable)
def start_with(self, *args, **kw):
    """Prepends a sequence of values to an observable sequence with an
    optional scheduler and an argument list of values to prepend.

    1 - source.start_with(1, 2, 3)
    2 - source.start_with(Scheduler.timeout, 1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    scheduler = kw.get("scheduler")

    if not scheduler and isinstance(args[0], Scheduler):
        scheduler = args[0]
        args = args[1:]
    else:
        scheduler = immediate_scheduler

    sequence = [Observable.from_(args, scheduler), self]
    return Observable.concat(sequence)
