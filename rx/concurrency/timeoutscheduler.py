from threading import Timer
from datetime import timedelta

from rx import disposable
from rx.core import typing
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable

from .schedulerbase import SchedulerBase


class TimeoutScheduler(SchedulerBase):
    """A scheduler that schedules work via a timed callback based upon platform."""

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None):
        """Schedules an action to be executed."""

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        timer = Timer(0, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose():
            timer.cancel()
        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_relative(self, duetime, action: typing.ScheduledAction, state: typing.TState = None):
        """Schedules an action to be executed after duetime."""

        scheduler = self
        timespan = self.to_timedelta(duetime)
        if timespan == timedelta(0):
            return scheduler.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        seconds = timespan.total_seconds()
        timer = Timer(seconds, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose():
            timer.cancel()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_absolute(self, duetime, action: typing.ScheduledAction, state: typing.TState = None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)


timeout_scheduler = TimeoutScheduler()
