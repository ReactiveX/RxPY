from typing import Any

from rx.core import typing
from rx.core import Observable, AnonymousObservable
from rx.concurrency import immediate_scheduler


def empty() -> Observable:
    """Returns an empty observable sequence.

    1 - res = rx.Observable.empty()

    Returns an observable sequence with no elements.
    """

    def subscribe(observer: typing.Observer, scheduler: typing.Scheduler = None) -> typing.Disposable:
        scheduler = scheduler or immediate_scheduler

        def action(_: typing.Scheduler, __: Any) -> None:
            observer.on_completed()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
