from datetime import datetime, timedelta
from typing import Any, Union

from rx.core import Scheduler, Disposable, typing, abc
from rx.disposables import MultipleAssignmentDisposable
from rx.internal.basic import default_now


class SchedulerBase(Scheduler):
    """Provides a set of static properties to access commonly used
    schedulers.
    """

    def invoke_action(self, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        ret = action(self, state)
        if isinstance(ret, abc.Disposable):
            return ret

        return Disposable.empty()

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        """Schedules a periodic piece of work.

        Args:
            period -- Period in seconds or timedelta for running the
                work periodically.
            action -- Action to be executed.
            state -- [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort)."""

        disposable = MultipleAssignmentDisposable()
        state = [state]

        def invoke_action(scheduler, _):
            if disposable.is_disposed:
                return

            new_state = action(state[0])
            if new_state is not None:
                state[0] = new_state
            disposable.disposable = self.schedule_relative(period, invoke_action, state)

        disposable.disposable = self.schedule_relative(period, invoke_action, state)
        return disposable

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.
        """

        return default_now()

    @classmethod
    def to_seconds(cls, timespan: Union[float, timedelta, datetime]) -> float:
        """Converts time value to seconds"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.utcfromtimestamp(0)
            timespan = timespan.total_seconds()
        elif isinstance(timespan, timedelta):
            timespan = timespan.total_seconds()

        return timespan

    @classmethod
    def to_datetime(cls, duetime: Union[float, timedelta, datetime]) -> datetime:
        """Converts time value to datetime"""

        if isinstance(duetime, timedelta):
            duetime = datetime.utcfromtimestamp(0) + duetime
        elif not isinstance(duetime, datetime):
            duetime = datetime.utcfromtimestamp(duetime)

        return duetime

    @classmethod
    def to_timedelta(cls, timespan: Union[float, timedelta, datetime]) -> timedelta:
        """Converts time value to timedelta"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.utcfromtimestamp(0)
        elif not isinstance(timespan, timedelta):
            timespan = timedelta(seconds=timespan)

        return timespan

    @classmethod
    def normalize(cls, timespan: typing.RelativeTime):
        """Normalizes the specified timespan value to a positive value.

        Args:
            timespan: The time span value to normalize.

        Returns:
            The specified timespan value if it is zero or positive;
            otherwise, 0
        """

        nospan = timedelta(0) if isinstance(timespan, timedelta) else 0.0
        if not timespan or timespan < nospan:
            timespan = nospan

        return timespan
