from typing import Any, Optional

from rx.core import Observable, abc
from rx.scheduler import ImmediateScheduler


def _throw(exception: Exception, scheduler: Optional[abc.SchedulerBase] = None) -> Observable:
    exception = exception if isinstance(exception, Exception) else Exception(exception)

    def subscribe(observer: abc.ObserverBase, scheduler: Optional[abc.SchedulerBase] = None) -> abc.DisposableBase:
        _scheduler = scheduler or ImmediateScheduler.singleton()

        def action(scheduler: abc.SchedulerBase, state: Any):
            observer.on_error(exception)

        return _scheduler.schedule(action)

    return Observable(subscribe)
