from datetime import datetime
from typing import Any, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@curry_flip
def take_until_with_time_(
    source: Observable[_T],
    end_time: typing.AbsoluteOrRelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Takes elements for the specified duration until the specified end
    time, using the specified scheduler to run timers.

    Examples:
        >>> source.pipe(take_until_with_time(dt))
        >>> take_until_with_time(5.0)(source)

    Args:
        source: Source observable to take elements from.
        end_time: Absolute or relative time when to complete.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence with the elements taken
        until the specified end time.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        def action(scheduler: abc.SchedulerBase, state: Any = None):
            observer.on_completed()

        if isinstance(end_time, datetime):
            task = _scheduler.schedule_absolute(end_time, action)
        else:
            task = _scheduler.schedule_relative(end_time, action)

        return CompositeDisposable(
            task, source.subscribe(observer, scheduler=scheduler_)
        )

    return Observable(subscribe)


__all__ = ["take_until_with_time_"]
