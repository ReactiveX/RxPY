from typing import Any

from reactivex import Observable, abc
from reactivex.scheduler import ImmediateScheduler


def empty_(scheduler: abc.SchedulerBase | None = None) -> Observable[Any]:
    def subscribe(
        observer: abc.ObserverBase[Any], scheduler_: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or ImmediateScheduler.singleton()

        def action(_: abc.SchedulerBase, __: Any) -> None:
            observer.on_completed()

        return _scheduler.schedule(action)

    return Observable(subscribe)


__all__ = ["empty_"]
