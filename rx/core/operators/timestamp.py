from typing import Callable, NamedTuple, Any, Optional
from datetime import datetime

from rx import defer
from rx.core import Observable, typing
from rx.scheduler import TimeoutScheduler
from rx import operators


class Timestamp(NamedTuple):
    value: Any
    timestamp: datetime


def _timestamp(scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Observable]:
    def timestamp(source: Observable) -> Observable:
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
            mapper = operators.map(lambda value: Timestamp(value=value, timestamp=_scheduler.now))

            return source.pipe(mapper)
        return defer(factory)
    return timestamp
