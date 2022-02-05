from datetime import timedelta
from typing import Any, Callable, NamedTuple, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc
from rx.scheduler import TimeoutScheduler

_T = TypeVar("_T")


class TimeInterval(NamedTuple):
    value: Any
    interval: timedelta


def time_interval(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def time_interval(source: Observable[_T]) -> Observable[_T]:
        """Records the time interval between consecutive values in an
        observable sequence.

            >>> res = time_interval(source)

        Return:
            An observable sequence with time interval information on
            values.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            last = _scheduler.now

            def mapper(value: _T) -> TimeInterval:
                nonlocal last

                now = _scheduler.now
                span = now - last
                last = now
                return TimeInterval(value=value, interval=span)

            return source.pipe(ops.map(mapper)).subscribe(observer, _scheduler)

        return Observable(subscribe)

    return time_interval
