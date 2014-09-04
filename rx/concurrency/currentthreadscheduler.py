# Current Thread Scheduler

import time
import logging
from datetime import timedelta

from rx.internal import PriorityQueue

from .scheduler import Scheduler
from .scheduleditem import ScheduledItem

log = logging.getLogger('Rx')

class Trampoline(object):
    def __init__(self, scheduler):
        self.queue = PriorityQueue(4)
        self.scheduler = scheduler

    def enqueue(self, item):
        return self.queue.enqueue(item)

    def dispose(self):
        self.queue = None

    def run(self):
        while self.queue.length > 0:
            item = self.queue.dequeue()
            if not item.is_cancelled():
                diff = item.duetime - self.scheduler.now()
                while diff > timedelta(0):
                    seconds = diff.seconds + diff.microseconds / 1E6 + diff.days * 86400
                    log.info("Trampoline:run(), Sleeping: %s" % seconds)
                    time.sleep(seconds)
                    diff = item.duetime - self.scheduler.now()

                if not item.is_cancelled():
                    item.invoke()

class CurrentThreadScheduler(Scheduler):
    """Represents an object that schedules units of work on the current thread."""

    def __init__(self):
        """Gets a scheduler that schedules work as soon as possible on the current thread."""
        self.queue = 0 # Must be different from None, FIXME:

    def schedule(self, action, state=None):
        log.debug("CurrentThreadScheduler.schedule(state=%s)", state)
        return self.schedule_relative(timedelta(0), action, state)

    def schedule_relative(self, duetime, action, state=None):
        log.debug("CurrentThreadScheduler.schedule_relative(duetime=%s, state=%s)" % (duetime, state))
        dt = self.now() + Scheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)

        if not self.queue:
            self.queue = Trampoline(self)
            try:
                self.queue.enqueue(si)
                self.queue.run()
            finally:
                self.queue.dispose()
                self.queue = None
        else:
            self.queue.enqueue(si)

        return si.disposable

    def schedule_absolute(self, duetime, action, state=None):
        return self.schedule_relative(duetime - self.now(), action, state=None)

    def schedule_required(self):
        return self.queue is None

    def ensure_trampoline(self, action):
        """Method for testing the CurrentThreadScheduler"""
        
        if self.queue is None:
            return self.schedule(action)
        else:
            return action(self, None)

Scheduler.current_thread = current_thread_scheduler = CurrentThreadScheduler()