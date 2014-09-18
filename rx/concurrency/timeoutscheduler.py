import logging
from threading import Timer
from datetime import timedelta

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable

from .scheduler import Scheduler

log = logging.getLogger("Rx")

class TimeoutScheduler(Scheduler):
    """A scheduler that schedules work via a timed callback based upon platform."""

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        scheduler = self
        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)
        timer = Timer(0, interval)
        timer.start()

        def dispose():
            timer.cancel()
        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        scheduler = self
        timespan = self.to_timedelta(duetime)
        if timespan == timedelta(0):
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()
        def interval():
            disposable.disposable = action(scheduler, state)

        seconds = timespan.total_seconds()
        log.debug("timeout: %s", seconds)
        timer = Timer(seconds, interval)
        timer.start()

        def dispose():
            timer.cancel()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now(), action, state)

Scheduler.timeout = timeout_scheduler = TimeoutScheduler()
