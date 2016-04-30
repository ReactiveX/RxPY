import logging

eventlet = None

from rx.core import Disposable
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

log = logging.getLogger("Rx")


class EventLetEventScheduler(SchedulerBase):
    """A scheduler that schedules work via the eventlet event loop.

    http://eventlet.net/
    """

    def __init__(self):
        # Lazy import
        global eventlet
        import eventlet
        import eventlet.hubs

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        timer = [eventlet.spawn(interval)]

        def dispose():
            timer[0].kill()

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = self.to_relative(duetime)/1000.0
        if not seconds:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        log.debug("timeout: %s", seconds)
        timer = [eventlet.spawn_after(seconds, interval)]

        def dispose():
            # nonlocal timer
            timer[0].kill()

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

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

        scheduler = self
        seconds = self.to_relative(period)/1000.0
        if not seconds:
            return scheduler.schedule(action, state)

        def interval():
            new_state = action(scheduler, state)
            scheduler.schedule_periodic(period, action, new_state)

        log.debug("timeout: %s", seconds)
        timer = [eventlet.spawn_after(seconds, interval)]

        def dispose():
            timer[0].kill()

        return Disposable.create(dispose)

    @property
    def now(self):
        """Represents a notion of time for this scheduler. Tasks being scheduled
        on a scheduler will adhere to the time denoted by this property."""

        return self.to_datetime(eventlet.hubs.hub.time.time())
