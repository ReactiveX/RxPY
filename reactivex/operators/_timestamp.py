from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, Optional, TypeVar

from reactivex import Observable, abc, defer, operators
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@dataclass
class Timestamp(Generic[_T]):
    value: _T
    timestamp: datetime


def timestamp_(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[Timestamp[_T]]]:
    def timestamp(source: Observable[Any]) -> Observable[Timestamp[_T]]:
        """Records the timestamp for each value in an observable sequence.

        Examples:
            >>> timestamp(source)

        Produces objects with attributes `value` and `timestamp`, where
        value is the original value.

        Args:
            source: Observable source to timestamp.

        Returns:
            An observable sequence with timestamp information on values.
        """

        def factory(scheduler_: Optional[abc.SchedulerBase] = None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            def mapper(value: _T) -> Timestamp[_T]:
                return Timestamp(value=value, timestamp=_scheduler.now)

            return source.pipe(operators.map(mapper))

        return defer(factory)

    return timestamp


__all__ = ["timestamp_"]
