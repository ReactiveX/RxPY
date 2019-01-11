from typing import Any

from rx.core import typing
from rx.core import Observable, AnonymousObservable
from rx.concurrency import immediate_scheduler


def _empty(scheduler: typing.Scheduler = None) -> Observable:
    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None) -> typing.Disposable:
        _scheduler = scheduler or scheduler_ or immediate_scheduler

        def action(_: typing.Scheduler, __: Any) -> None:
            observer.on_completed()

        return _scheduler.schedule(action)
    return AnonymousObservable(subscribe)
