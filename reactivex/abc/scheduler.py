from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable, Optional, TypeVar, Union

from .disposable import DisposableBase

_TState = TypeVar("_TState")  # Can be anything

AbsoluteTime = Union[datetime, float]
RelativeTime = Union[timedelta, float]
AbsoluteOrRelativeTime = Union[datetime, timedelta, float]
ScheduledAction = Callable[
    ["SchedulerBase", Optional[_TState]],
    Optional[DisposableBase],
]


class SchedulerBase(ABC):
    """Scheduler abstract base class."""

    __slots__ = ()

    @property
    @abstractmethod
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return NotImplemented

    @abstractmethod
    def schedule(
        self, action: ScheduledAction[_TState], state: Optional[_TState] = None
    ) -> DisposableBase:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @abstractmethod
    def schedule_relative(
        self,
        duetime: RelativeTime,
        action: ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> DisposableBase:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @abstractmethod
    def schedule_absolute(
        self,
        duetime: AbsoluteTime,
        action: ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> DisposableBase:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_seconds(cls, value: AbsoluteOrRelativeTime) -> float:
        """Converts time value to seconds. This method handles both absolute
        (datetime) and relative (timedelta) values. If the argument is already
        a float, it is simply returned unchanged.

        Args:
            value: the time value to convert to seconds.

        Returns:
            The value converted to seconds.
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_datetime(cls, value: AbsoluteOrRelativeTime) -> datetime:
        """Converts time value to datetime. This method handles both absolute
        (float) and relative (timedelta) values. If the argument is already
        a datetime, it is simply returned unchanged.

        Args:
            value: the time value to convert to datetime.

        Returns:
            The value converted to datetime.
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_timedelta(cls, value: AbsoluteOrRelativeTime) -> timedelta:
        """Converts time value to timedelta. This method handles both absolute
        (datetime) and relative (float) values. If the argument is already
        a timedelta, it is simply returned unchanged. If the argument is an
        absolute time, the result value will be the timedelta since the epoch,
        January 1st, 1970, 00:00:00.

        Args:
            value: the time value to convert to timedelta.

        Returns:
            The value converted to timedelta.
        """

        return NotImplemented


__all__ = [
    "SchedulerBase",
    "AbsoluteTime",
    "RelativeTime",
    "AbsoluteOrRelativeTime",
    "ScheduledAction",
]
