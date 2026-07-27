from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from reactivex import Observable, abc, defer, operators
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@dataclass
class Timestamp(Generic[_T]):
    value: _T
    timestamp: datetime


@curry_flip
def timestamp_(
    source: Observable[_T],
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[Timestamp[_T]]:
    """Records the timestamp for each value in an observable sequence.

    Examples:
        >>> result = source.pipe(timestamp())
        >>> result = timestamp()(source)

    Produces objects with attributes `value` and `timestamp`, where
    value is the original value.

    Args:
        source: Observable source to timestamp.
        scheduler: Optional scheduler to use for timestamping.

    Returns:
        An observable sequence with timestamp information on values.
    """

    def factory(scheduler_: abc.SchedulerBase | None = None):
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        def mapper(value: _T) -> Timestamp[_T]:
            return Timestamp(value=value, timestamp=_scheduler.now)

        return source.pipe(operators.map(mapper))

    return defer(factory)


__all__ = ["timestamp_"]
