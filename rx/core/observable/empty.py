from typing import Any

from rx.core import typing
from rx.core import Observable, AnonymousObservable
from rx.concurrency import immediate_scheduler


def empty(scheduler: typing.Scheduler = None) -> Observable:
    """Returns an empty observable sequence.

    Example:
        >>> obs = empty()

    Args:
        scheduler: Scheduler to send the termination call on.

    Returns:
        An observable sequence with no elements.
    """

    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None) -> typing.Disposable:
        scheduler = scheduler or scheduler_ or immediate_scheduler

        def action(_: typing.Scheduler, __: Any) -> None:
            observer.on_completed()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
