from typing import Any, Callable

from rx.core import ObservableBase, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.core.bases.scheduler import Scheduler


def return_value(value: Any) -> ObservableBase:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    example
    res = rx.Observable.return(42)
    res = rx.Observable.return(42, rx.Scheduler.timeout)

    Keyword arguments:
    value -- Single element in the resulting observable sequence.

    Returns an observable sequence containing the single specified
    element.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        def action(scheduler, state=None):
            observer.send(value)
            observer.close()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)


def from_callable(supplier: Callable) -> ObservableBase:
    """Returns an observable sequence that contains a single element
    generate from a supplier, using the specified scheduler to send out
    observer messages.

    example
    res = rx.Observable.from_callable(lambda: calculate_value())
    res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error

    Keyword arguments:
    value -- Single element in the resulting observable sequence.

    Returns an observable sequence containing the single specified
    element derived from the supplier
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        def action(_: Scheduler, __: Any=None):
            nonlocal observer

            try:
                observer.send(supplier())
                observer.close()
            except Exception as e:
                observer.throw(e)
        return scheduler.schedule(action)

    return AnonymousObservable(subscribe)
