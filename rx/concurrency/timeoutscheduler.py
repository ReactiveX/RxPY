import logging
from threading import Timer

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable

from .scheduler import Scheduler

log = logging.getLogger("Rx")

class TimeoutScheduler(Scheduler):
    """A scheduler that schedules work via a timed callback based upon platform."""

    def schedule(self, action, state=None):
        scheduler = self
        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)
        timer = [Timer(0, interval)]
        timer[0].start()

        def dispose():
            # nonlocal timer
            timer[0].cancel()
        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        scheduler = self
        dt = Scheduler.normalize(duetime)
        if dt == 0:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()
        def interval():
            disposable.disposable = action(scheduler, state)

        if isinstance(dt, int):
            seconds = dt/1000.0
        else:
            seconds = dt.seconds+dt.microseconds/1000000.0
        log.debug("timeout: %s", seconds)
        timer = [Timer(seconds, interval)]
        timer[0].start()

        def dispose():
            # nonlocal timer
            timer[0].cancel()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        return self.schedule_relative(duetime - self.now(), action, state)

Scheduler.timeout = timeout_scheduler = TimeoutScheduler()
