from datetime import timedelta
from typing import Any

from rx.core import typing
from rx.internal.exceptions import WouldBlockException
from .schedulerbase import SchedulerBase


class ImmediateScheduler(SchedulerBase):
    def schedule(self, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        return self.invoke_action(action, state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime."""

        duetime = self.to_timedelta(duetime)
        if duetime > timedelta(0):
            raise WouldBlockException()

        return self.invoke_action(action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)


immediate_scheduler = ImmediateScheduler()
