from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Optional, TypeVar

from reactivex import Observable, abc, defer, operators
from reactivex.curry import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@dataclass
class Timestamp(Generic[_T]):
    value: _T
    timestamp: datetime


@curry_flip(1)
def timestamp_(
    source: Observable[_T],
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[Timestamp[_T]]:
    """Records the timestamp for each value in an observable sequence.

    Examples:
        >>> timestamp(source)

    Produces objects with attributes `value` and `timestamp`, where
    value is the original value.

    Args:
        source: Observable source to timestamp.

    Returns:
        An observable sequence with timestamp information on values.
        Each emitted item is a Timestamp object with `.value` and
        `.timestamp` attributes
    """

    def factory(scheduler_: Optional[abc.SchedulerBase] = None):
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        def mapper(value: _T) -> Timestamp[_T]:
            return Timestamp(value=value, timestamp=_scheduler.now)

        return source.pipe(operators.map(mapper))

    return defer(factory)


__all__ = ["timestamp_"]
