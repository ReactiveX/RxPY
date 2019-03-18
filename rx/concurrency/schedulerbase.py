from datetime import datetime, timedelta
from typing import Optional

from rx.core import typing
from rx.disposable import Disposable, MultipleAssignmentDisposable
from rx.internal.basic import default_now
from rx.internal.constants import DELTA_ZERO, UTC_ZERO

class SchedulerBase(typing.Scheduler):
    """Provides a set of static properties to access commonly used
    schedulers.
    """

    def invoke_action(self,
                      action: typing.ScheduledAction,
                      state: Optional[typing.TState] = None
                      ) -> typing.Disposable:
        ret = action(self, state)
        if isinstance(ret, typing.Disposable):
            return ret

        return Disposable()

    def schedule_periodic(self,
                          period: typing.RelativeTime,
                          action: typing.ScheduledPeriodicAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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

        disp = MultipleAssignmentDisposable()

        def invoke_periodic(scheduler: typing.Scheduler, _: typing.TState) -> Optional[Disposable]:
            nonlocal state

            if disp.is_disposed:
                return None

            if period:
                disp.disposable = self.schedule_relative(period, invoke_periodic, None)

            try:
                new_state = action(state)
            except Exception:
                disp.dispose()
                raise

            if state is not None:
                state = new_state

            return None

        disp.disposable = self.schedule_relative(period, invoke_periodic, None)
        return disp

    @property
    def now(self) -> datetime:
        """Returns the current time.

        Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by
        this property.
        """

        return default_now()

    @classmethod
    def to_seconds(cls, timespan: typing.AbsoluteOrRelativeTime) -> float:
        """Converts time value to seconds"""

        if isinstance(timespan, datetime):
            timespan = timespan - UTC_ZERO
            timespan = timespan.total_seconds()
        elif isinstance(timespan, timedelta):
            timespan = timespan.total_seconds()

        return timespan

    @classmethod
    def to_datetime(cls, duetime: typing.AbsoluteOrRelativeTime) -> datetime:
        """Converts time value to datetime"""

        if isinstance(duetime, timedelta):
            duetime = UTC_ZERO + duetime
        elif not isinstance(duetime, datetime):
            duetime = datetime.utcfromtimestamp(duetime)

        return duetime

    @classmethod
    def to_timedelta(cls, timespan: typing.AbsoluteOrRelativeTime) -> timedelta:
        """Converts time value to timedelta"""

        if isinstance(timespan, datetime):
            timespan = timespan - UTC_ZERO
        elif not isinstance(timespan, timedelta):
            timespan = timedelta(seconds=timespan)

        return timespan

    @classmethod
    def normalize(cls, timespan: typing.RelativeTime) -> typing.RelativeTime:
        """Normalizes the specified timespan value to a positive value.

        Args:
            timespan: The time span value to normalize.

        Returns:
            The specified timespan value if it is zero or positive;
            otherwise, 0.0
        """

        if isinstance(timespan, timedelta):
            if not timespan or timespan < DELTA_ZERO:
                return DELTA_ZERO

        elif isinstance(timespan, float):
            if not timespan or timespan < 0.0:
                return 0.0

        return timespan
