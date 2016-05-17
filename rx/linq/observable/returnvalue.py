from rx.core import Observable, AnonymousObservable

from rx.concurrency import current_thread_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias="just")
def return_value(cls, value, scheduler=None):
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    example
    res = rx.Observable.return(42)
    res = rx.Observable.return(42, rx.Scheduler.timeout)

    Keyword arguments:
    value -- Single element in the resulting observable sequence.
    scheduler -- [Optional] Scheduler to send the single element on. If
        not specified, defaults to Scheduler.immediate.

    Returns an observable sequence containing the single specified
    element.
    """

    scheduler = scheduler or current_thread_scheduler

    def subscribe(observer):
        def action(scheduler, state=None):
            observer.on_next(value)
            observer.on_completed()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
