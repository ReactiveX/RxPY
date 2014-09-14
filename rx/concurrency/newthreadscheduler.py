import time
import threading
import logging
from datetime import timedelta

from .scheduler import Scheduler

log = logging.getLogger('Rx')

class NewThreadScheduler(Scheduler):
    """Creates an object that schedules each unit of work on a separate thread."""

    def __init__(self):
        """Gets a scheduler that schedules work as soon as possible on the current thread."""
        self.queue = 0 # Must be different from None, FIXME:

    def schedule(self, action, state=None):
        log.debug("NewThreadScheduler.schedule(state=%s)", state)
        disposable = SingleAssignmentDisposable()
        disposed = [False]

        def interval():
            if not disposed[0]:
                disposable.disposable = action(scheduler, state)

        t = threading.Thread(target=interval, args=(self, state))
        t.start()
        
        def dispose():
            disponsed[0] = True

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        log.debug("CurrentThreadScheduler.schedule_relative(duetime=%s, state=%s)" % (duetime, state))
        dt = self.now() + Scheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)


    def schedule_absolute(self, duetime, action, state=None):
        return self.schedule_relative(duetime - self.now(), action, state=None)


Scheduler.new_thread = new_thread_scheduler = NewThreadScheduler()