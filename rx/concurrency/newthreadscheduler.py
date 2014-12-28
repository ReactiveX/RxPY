import logging
import threading
from threading import Timer
from datetime import timedelta

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable

from .scheduler import Scheduler

log = logging.getLogger('Rx')


class NewThreadScheduler(Scheduler):
    """Creates an object that schedules each unit of work on a separate thread.
    """

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        log.debug("NewThreadScheduler.schedule(state=%s)", state)
        disposable = SingleAssignmentDisposable()
        disposed = [False]

        def interval(scheduler, state):
            if not disposed[0]:
                disposable.disposable = action(scheduler, state)

        t = threading.Thread(target=interval, args=(self, state))
        t.start()

        def dispose():
            disposed[0] = True

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
        """Schedules an action to be executed at duetime."""

        return self.schedule_relative(duetime - self.now(), action, state=None)

Scheduler.new_thread = new_thread_scheduler = NewThreadScheduler()