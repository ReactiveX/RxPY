from datetime import datetime

from rx.core import typing
from .scheduler import UTC_ZERO
from .virtualtimescheduler import VirtualTimeScheduler


class HistoricalScheduler(VirtualTimeScheduler):
    """Provides a virtual time scheduler that uses datetime for absolute time
    and timedelta for relative time."""

    def __init__(self, initial_clock: datetime = None) -> None:
        """Creates a new historical scheduler with the specified initial clock
        value.

        Args:
            initial_clock: Initial value for the clock.
        """

        super().__init__(initial_clock or UTC_ZERO)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self._clock

    @classmethod
    def add(cls,
            absolute: typing.AbsoluteTime,
            relative: typing.RelativeTime
            ) -> typing.AbsoluteTime:
        """Adds a relative time value to an absolute time value.

        Args:
            absolute: Absolute virtual time value.
            relative: Relative virtual time value to add.

        Returns:
            The resulting absolute virtual time sum value.
        """

        return cls.to_datetime(absolute) + cls.to_timedelta(relative)
