from datetime import datetime
from typing import Any, Callable, NamedTuple, Optional

from rx import defer, operators
from rx.core import Observable, abc
from rx.scheduler import TimeoutScheduler


class Timestamp(NamedTuple):
    value: Any
    timestamp: datetime


def _timestamp(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[Any]], Observable[Timestamp]]:
    def timestamp(source: Observable[Any]) -> Observable[Timestamp]:
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

        def factory(scheduler_=None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            mapper = operators.map(
                lambda value: Timestamp(value=value, timestamp=_scheduler.now)
            )

            return source.pipe(mapper)

        return defer(factory)

    return timestamp
