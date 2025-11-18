from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

from .disposable import DisposableBase
from .scheduler import RelativeTime, ScheduledAction

_TState = TypeVar("_TState")  # Can be anything

ScheduledPeriodicAction = Callable[[_TState | None], _TState | None]
ScheduledSingleOrPeriodicAction = (
    ScheduledAction[_TState] | ScheduledPeriodicAction[_TState]
)


class PeriodicSchedulerBase(ABC):
    """PeriodicScheduler abstract base class."""

    __slots__ = ()

    @abstractmethod
    def schedule_periodic(
        self,
        period: RelativeTime,
        action: ScheduledPeriodicAction[_TState],
        state: _TState | None = None,
    ) -> DisposableBase:
        """Schedules a periodic piece of work.

        Args:
            period: Period in seconds or timedelta for running the
                work periodically.
            action: Action to be executed.
            state: [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort).
        """

        return NotImplemented


__all__ = [
    "PeriodicSchedulerBase",
    "ScheduledPeriodicAction",
    "ScheduledSingleOrPeriodicAction",
    "RelativeTime",
]
