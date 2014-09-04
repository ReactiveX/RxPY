import logging
from datetime import datetime, timedelta

import gevent
import gevent.core

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.concurrency.scheduler import Scheduler

log = logging.getLogger("Rx")

class GEventScheduler(Scheduler):
    """A scheduler that schedules work via the GEvent event loop.

    http://www.gevent.org/
    """

    def schedule(self, action, state=None):
        scheduler = self
        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)

        timer = [gevent.spawn(interval)]

        def dispose():
            timer[0].kill()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = GEventScheduler.normalize(duetime)
        if seconds == 0:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)

        log.debug("timeout: %s", seconds)
        timer = [gevent.spawn_later(seconds, interval)]

        def dispose():
            # nonlocal timer
            timer[0].kill()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        return self.schedule_relative(duetime - self.now(), action, state)

    def default_now(self):
        return gevent.core.time()

    @classmethod
    def normalize(cls, timespan):
        """GEvent operates with seconds as floats"""
        nospan = 0

        if isinstance(timespan, timedelta):
            seconds = timespan.seconds+timespan.microseconds/1000000.0

        elif isinstance(timespan, datetime):
            seconds = timespan.totimestamp()
        else:
            seconds = timespan

        if not timespan or timespan < nospan:
            seconds = nospan

        return seconds

