from .schedulerbase import UTC_ZERO
from .virtualtimescheduler import VirtualTimeScheduler


class HistoricalScheduler(VirtualTimeScheduler):
    """Provides a virtual time scheduler that uses datetime for absolute time
    and timedelta for relative time."""

    def __init__(self, initial_clock=None):
        """Creates a new historical scheduler with the specified initial clock
        value.

        Keyword arguments:
        initial_clock -- {Number} Initial value for the clock.
        """

        super().__init__(initial_clock or UTC_ZERO)

    @property
    def now(self):
        """Represents a notion of time for this scheduler. Tasks being scheduled
        on a scheduler will adhere to the time denoted by this property."""

        return self._clock

    @staticmethod
    def add(absolute, relative):
        """Adds a relative time value to an absolute time value.

        Keyword arguments:
        absolute -- {datetime} Absolute virtual time value.
        relative -- {timedelta} Relative virtual time value to add.

        Returns resulting absolute virtual time sum value."""

        return absolute + relative
