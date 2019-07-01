from typing import Any, Callable, Optional

from rx.core import typing
from rx.core import Observable
from rx.scheduler import CurrentThreadScheduler
from rx.core.abc.scheduler import Scheduler


def _return_value(value: Any, scheduler: Optional[typing.Scheduler] = None) -> Observable:
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

    def subscribe(observer: typing.Observer, scheduler_: Optional[typing.Scheduler] = None) -> typing.Disposable:
        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()

        def action(scheduler: typing.Scheduler, state: Any = None):
            observer.on_next(value)
            observer.on_completed()

        return _scheduler.schedule(action)
    return Observable(subscribe)


def _from_callable(supplier: Callable[[], Any], scheduler: Optional[typing.Scheduler] = None) -> Observable:
    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None):
        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()

        def action(_: Scheduler, __: Any = None):
            nonlocal observer

            try:
                observer.on_next(supplier())
                observer.on_completed()
            except Exception as e:  # pylint: disable=broad-except
                observer.on_error(e)
        return _scheduler.schedule(action)

    return Observable(subscribe)
