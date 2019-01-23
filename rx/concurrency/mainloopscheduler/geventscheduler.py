import logging

from rx import disposable
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

gevent = None
log = logging.getLogger("Rx")


class GEventScheduler(SchedulerBase):
    """A scheduler that schedules work via the GEvent event loop.

    http://www.gevent.org/
    """

    def __init__(self):
        # Lazy import gevent
        global gevent
        import gevent
        import gevent.core

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        timer = [gevent.spawn(interval)]

        def dispose():
            timer[0].kill()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = self.to_seconds(duetime)
        if not seconds:
            return scheduler.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = action(scheduler, state)

        log.debug("timeout: %s", seconds)
        timer = [gevent.spawn_later(seconds, interval)]

        def dispose():
            # nonlocal timer
            timer[0].kill()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)

    @property
    def now(self):
        """Represents a notion of time for this scheduler. Tasks being scheduled
        on a scheduler will adhere to the time denoted by this property."""

        return self.to_datetime(gevent.core.time())
