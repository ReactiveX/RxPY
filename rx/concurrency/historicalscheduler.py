from datetime import datetime

from .virtualtimescheduler import VirtualTimeScheduler

class HistoricalScheduler(VirtualTimeScheduler):
    """Provides a virtual time scheduler that uses Date for absolute time and
    number for relative time."""

    def __init__(self, initial_clock, comparer):
        """Creates a new historical scheduler with the specified initial clock
        value.

        Keyword arguments:
        initial_clock -- {Number} Initial value for the clock.
        comparer -- {Function} Comparer to determine causality of events based
            on absolute time."""

        clock = 0 if not initial_clock else initial_clock
        cmp = comparer or default_sub_comparer

        super(HistoricalScheduler, self).__init__(clock, cmp)

    @staticmethod
    def add(absolute, relative):
        """Adds a relative time value to an absolute time value.

        Keyword arguments:
        absolute -- {Number} Absolute virtual time value.
        relative -- {Number} Relative virtual time value to add.

        Returns resulting absolute virtual time sum value."""

        return absolute + relative

    @staticmethod
    def to_datetime_offset(absolute):
        return datetime.from_timestamp(absolute)

    def to_relative(self, time_span):
        """Converts the Timespan value to a relative virtual time value.

        Keyword arguments:
        time_span -- {Number} Time_span value to convert.

        Returns corresponding relative virtual time value."""

        return time_span
