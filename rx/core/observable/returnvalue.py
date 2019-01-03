from typing import Any, Callable

from rx.core import typing
from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.core.abc.scheduler import Scheduler


def return_value(value: Any, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    Examples:
        >>> res = return(42)
        >>> res = return(42, rx.Scheduler.timeout)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified
        element.
    """

    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None) -> typing.Disposable:
        _scheduler = scheduler or scheduler_ or current_thread_scheduler

        def action(scheduler: typing.Scheduler, state: Any = None):
            observer.on_next(value)
            observer.on_completed()

        return _scheduler.schedule(action)
    return AnonymousObservable(subscribe)


def from_callable(supplier: Callable, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element
    generate from a supplier, using the specified scheduler to send out
    observer messages.

    Examples:
        >>> res = from_callable(lambda: calculate_value())
        >>> res = from_callable(lambda: 1 / 0) # emits an error

    Args:
        value: Single element in the resulting observable sequence.
        scheduler: Scheduler to schedule the values on.

    Returns:
        An observable sequence containing the single specified
        element derived from the supplier
    """

    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None):
        scheduler = scheduler or scheduler_ or current_thread_scheduler

        def action(_: Scheduler, __: Any = None):
            nonlocal observer

            try:
                observer.on_next(supplier())
                observer.on_completed()
            except Exception as e:  # pylint: disable=broad-except
                observer.on_error(e)
        return scheduler.schedule(action)

    return AnonymousObservable(subscribe)
