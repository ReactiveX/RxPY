from rx.core import Observable, AnonymousObservable
from rx.concurrency import immediate_scheduler
from rx.core.bases.scheduler import Scheduler


def empty(scheduler: Scheduler=None) -> Observable:
    """Returns an empty observable sequence, using the specified scheduler
    to send out the single OnCompleted message.

    1 - res = rx.Observable.empty()
    2 - res = rx.Observable.empty(rx.Scheduler.timeout)

    scheduler -- Scheduler to send the termination call on.

    Returns an observable sequence with no elements.
    """

    scheduler = scheduler or immediate_scheduler

    def subscribe(observer):
        def action(scheduler, state):
            nonlocal observer

            observer.close()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)

