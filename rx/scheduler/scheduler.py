from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from rx.core import typing
from rx.disposable import Disposable
from rx.internal.basic import default_now
from rx.internal.constants import UTC_ZERO


class Scheduler(typing.Scheduler):
    """Base class for the various scheduler implementations in this package as
    well as the mainloop sub-package. This does not include an implementation
    of schedule_periodic, refer to PeriodicScheduler.
    """

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return default_now()

    @abstractmethod
    def schedule(self,
                 action: typing.ScheduledAction,
                 state: Optional[typing.TState] = None
                 ) -> typing.Disposable:
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
    def schedule_relative(self,
                          duetime: typing.RelativeTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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
    def schedule_absolute(self,
                          duetime: typing.AbsoluteTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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

    def invoke_action(self,
                      action: typing.ScheduledAction,
                      state: Optional[typing.TState] = None
                      ) -> typing.Disposable:
        """Invoke the given given action. This is typically called by instances
        of ScheduledItem.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object returned by the action, if any; or a new
            (no-op) disposable otherwise.
        """

        ret = action(self, state)
        if isinstance(ret, typing.Disposable):
            return ret

        return Disposable()

    @classmethod
    def to_seconds(cls, value: typing.AbsoluteOrRelativeTime) -> float:
        """Converts time value to seconds. This method handles both absolute
        (datetime) and relative (timedelta) values. If the argument is already
        a float, it is simply returned unchanged.

        Args:
            value: the time value to convert to seconds.

        Returns:
            The value converted to seconds.
        """

        if isinstance(value, datetime):
            value = value - UTC_ZERO

        if isinstance(value, timedelta):
            value = value.total_seconds()

        return value

    @classmethod
    def to_datetime(cls, value: typing.AbsoluteOrRelativeTime) -> datetime:
        """Converts time value to datetime. This method handles both absolute
        (float) and relative (timedelta) values. If the argument is already
        a datetime, it is simply returned unchanged.

        Args:
            value: the time value to convert to datetime.

        Returns:
            The value converted to datetime.
        """

        if isinstance(value, timedelta):
            value = UTC_ZERO + value
        elif not isinstance(value, datetime):
            value = datetime.utcfromtimestamp(value)

        return value

    @classmethod
    def to_timedelta(cls, value: typing.AbsoluteOrRelativeTime) -> timedelta:
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

        if isinstance(value, datetime):
            value = value - UTC_ZERO
        elif not isinstance(value, timedelta):
            value = timedelta(seconds=value)

        return value
