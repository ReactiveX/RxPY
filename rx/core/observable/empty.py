from typing import Any, Optional

from rx.core import typing
from rx.core import Observable
from rx.concurrency import immediate_scheduler


def _empty(scheduler: Optional[typing.Scheduler] = None) -> Observable:
    def subscribe(observer: typing.Observer, scheduler_: Optional[typing.Scheduler] = None) -> typing.Disposable:
        _scheduler = scheduler or scheduler_ or immediate_scheduler

        def action(_: typing.Scheduler, __: Any) -> None:
            observer.on_completed()

        return _scheduler.schedule(action)
    return Observable(subscribe)
