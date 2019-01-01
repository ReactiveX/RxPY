from typing import Callable
from datetime import datetime

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler


def take_until_with_time(end_time) -> Callable[[Observable], Observable]:
    """Takes elements for the specified duration until the specified end
    time, using the specified scheduler to run timers.

    Examples:
    1 - res = source.take_until_with_time(dt, [optional scheduler])
    2 - res = source.take_until_with_time(5000, [optional scheduler])

    Keyword Arguments:
    end_time -- {Number | Date} Time to stop taking elements from the source
        sequence. If this value is less than or equal to Date(), the
        result stream will complete immediately.
    scheduler -- {Scheduler} Scheduler to run the timer on.

    Returns an observable {Observable} sequence with the elements taken
    until the specified end time.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            scheduler = scheduler or timeout_scheduler

            if isinstance(end_time, datetime):
                scheduler_method = scheduler.schedule_absolute
            else:
                scheduler_method = scheduler.schedule_relative

            def action(scheduler, state):
                observer.on_completed()

            task = scheduler_method(end_time, action)
            return CompositeDisposable(task,  source.subscribe(observer, scheduler))
        return AnonymousObservable(subscribe)
    return partial
