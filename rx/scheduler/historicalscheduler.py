from datetime import datetime
from typing import Optional

from .scheduler import UTC_ZERO
from .virtualtimescheduler import VirtualTimeScheduler


class HistoricalScheduler(VirtualTimeScheduler):
    """Provides a virtual time scheduler that uses datetime for absolute time
    and timedelta for relative time."""

    def __init__(self, initial_clock: Optional[datetime] = None) -> None:
        """Creates a new historical scheduler with the specified initial clock
        value.

        Args:
            initial_clock: Initial value for the clock.
        """

        super().__init__(initial_clock or UTC_ZERO)
