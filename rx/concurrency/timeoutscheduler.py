from typing import Any
from threading import Timer
from datetime import timedelta

from rx.core import Disposable, typing
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable

from .schedulerbase import SchedulerBase


class TimeoutScheduler(SchedulerBase):
    """A scheduler that schedules work via a timed callback based upon platform."""

    def schedule(self, action: typing.ScheduledAction, state: Any = None):
        """Schedules an action to be executed."""

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        timer = Timer(0, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose():
            timer.cancel()
        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_relative(self, duetime, action: typing.ScheduledAction, state: Any = None):
        """Schedules an action to be executed after duetime."""

        scheduler = self
        timespan = self.to_timedelta(duetime)
        if timespan == timedelta(0):
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        seconds = timespan.total_seconds()
        timer = Timer(seconds, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose():
            timer.cancel()

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_absolute(self, duetime, action: typing.ScheduledAction, state: Any = None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)


timeout_scheduler = TimeoutScheduler()
