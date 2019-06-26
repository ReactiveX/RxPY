from typing import Any, Optional

from rx.core import typing
from rx.core import Observable

from rx.scheduler import ImmediateScheduler


def _throw(exception: Exception, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    exception = exception if isinstance(exception, Exception) else Exception(exception)

    def subscribe(observer: typing.Observer, scheduler: Optional[typing.Scheduler] = None) -> typing.Disposable:
        _scheduler = scheduler or ImmediateScheduler.singleton()

        def action(scheduler: typing.Scheduler, state: Any):
            observer.on_error(exception)

        return _scheduler.schedule(action)
    return Observable(subscribe)
