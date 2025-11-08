from typing import Any

from reactivex import Observable, abc
from reactivex.scheduler import ImmediateScheduler


def throw_(
    exception: str | Exception, scheduler: abc.SchedulerBase | None = None
) -> Observable[Any]:
    exception_ = exception if isinstance(exception, Exception) else Exception(exception)

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or ImmediateScheduler.singleton()

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            observer.on_error(exception_)

        return _scheduler.schedule(action)

    return Observable(subscribe)


__all__ = ["throw_"]
