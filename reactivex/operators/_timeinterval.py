from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Generic, Optional, TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@dataclass
class TimeInterval(Generic[_T]):
    value: _T
    interval: timedelta


def time_interval_(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[TimeInterval[_T]]]:
    def time_interval(source: Observable[_T]) -> Observable[TimeInterval[_T]]:
        """Records the time interval between consecutive values in an
        observable sequence.

            >>> res = time_interval(source)

        Return:
            An observable sequence with time interval information on
            values.
        """

        def subscribe(
            observer: abc.ObserverBase[TimeInterval[_T]],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            last = _scheduler.now

            def mapper(value: _T) -> TimeInterval[_T]:
                nonlocal last

                now = _scheduler.now
                span = now - last
                last = now
                return TimeInterval(value=value, interval=span)

            return source.pipe(ops.map(mapper)).subscribe(
                observer, scheduler=_scheduler
            )

        return Observable(subscribe)

    return time_interval
