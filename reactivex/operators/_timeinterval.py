from dataclasses import dataclass
from datetime import timedelta
from typing import Generic, TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@dataclass
class TimeInterval(Generic[_T]):
    value: _T
    interval: timedelta


@curry_flip
def time_interval_(
    source: Observable[_T],
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[TimeInterval[_T]]:
    """Records the time interval between consecutive values in an
    observable sequence.

    Examples:
        >>> res = source.pipe(time_interval())
        >>> res = time_interval()(source)

    Args:
        source: The source observable sequence.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence with time interval information on
        values.
    """

    def subscribe(
        observer: abc.ObserverBase[TimeInterval[_T]],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
        last = _scheduler.now

        def mapper(value: _T) -> TimeInterval[_T]:
            nonlocal last

            now = _scheduler.now
            span = now - last
            last = now
            return TimeInterval(value=value, interval=span)

        return source.pipe(ops.map(mapper)).subscribe(observer, scheduler=_scheduler)

    return Observable(subscribe)
