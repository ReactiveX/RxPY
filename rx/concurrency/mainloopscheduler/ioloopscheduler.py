import logging
from datetime import datetime

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.concurrency.scheduler import Scheduler

log = logging.getLogger("Rx")

class IOLoopScheduler(Scheduler):
    """A scheduler that schedules work via the Tornado I/O main event loop.

    http://tornado.readthedocs.org/en/latest/ioloop.html"""

    def __init__(self, loop=None):
        from tornado import ioloop # Lazy import
        self.loop = loop or ioloop.IOLoop.current()

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        scheduler = self
        disposable = SingleAssignmentDisposable()
        disposed = [False]

        def interval():
            if not disposed[0]:
                disposable.disposable = action(scheduler, state)

        self.loop.add_callback(interval)

        def dispose():
            # nonlocal
            disposed[0] = True

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = scheduler.to_relative(duetime)/1000.0
        if not seconds:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()
        def interval():
            disposable.disposable = action(scheduler, state)

        log.debug("timeout: %s", seconds)
        handle = self.loop.call_later(seconds, interval)

        def dispose():
            self.loop.remove_timeout(handle)

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now(), action, state)

    def now(self):
        """Represents a notion of time for this scheduler. Tasks being scheduled
        on a scheduler will adhere to the time denoted by this property."""

        return self.to_datetime(self.loop.time())

