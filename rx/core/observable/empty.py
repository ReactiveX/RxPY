from typing import Any, Optional

from rx.core import Observable, abc
from rx.scheduler import ImmediateScheduler


def _empty(scheduler: Optional[abc.SchedulerBase] = None) -> Observable:
    def subscribe(observer: abc.ObserverBase, scheduler_: Optional[abc.SchedulerBase] = None) -> abc.DisposableBase:

        _scheduler = scheduler or scheduler_ or ImmediateScheduler.singleton()

        def action(_: abc.SchedulerBase, __: Any) -> None:
            observer.on_completed()

        return _scheduler.schedule(action)

    return Observable(subscribe)
