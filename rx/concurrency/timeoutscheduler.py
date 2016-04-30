import logging
from threading import Timer
from datetime import timedelta

from rx.core import Scheduler, Disposable
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable

from .schedulerbase import SchedulerBase

log = logging.getLogger("Rx")


class TimeoutScheduler(SchedulerBase):
    """A scheduler that schedules work via a timed callback based upon platform."""

    def schedule(self, action, state=None):
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

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        scheduler = self
        timespan = self.to_timedelta(duetime)
        if timespan == timedelta(0):
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        seconds = timespan.total_seconds()
        log.debug("timeout: %s", seconds)
        timer = Timer(seconds, interval)
        timer.start()

        def dispose():
            timer.cancel()

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)

    def schedule_periodic(self, period, action, state=None):
        """Schedules a periodic piece of work by dynamically discovering the
        schedulers capabilities.

        Keyword arguments:
        period -- Period for running the work periodically.
        action -- Action to be executed.
        state -- [Optional] Initial state passed to the action upon the first
            iteration.

        Returns the disposable object used to cancel the scheduled recurring
        action (best effort)."""

        period /= 1000.0
        timer = [None]
        s = [state]

        def interval():
            new_state = action(s[0])
            if new_state is not None:  # Update state if other than None
                s[0] = new_state

            timer[0] = Timer(period, interval)
            timer[0].setDaemon(True)
            timer[0].start()

        timer[0] = Timer(period, interval)
        timer[0].setDaemon(True)
        timer[0].start()

        def dispose():
            timer[0].cancel()

        return Disposable.create(dispose)


Scheduler.timeout = timeout_scheduler = TimeoutScheduler()
