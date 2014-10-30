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
        while len(self.queue):
            item = self.queue.dequeue()
            if not item.is_cancelled():
                diff = item.duetime - self.scheduler.now()
                while diff > timedelta(0):
                    seconds = diff.seconds + diff.microseconds / 1E6 + diff.days * 86400
                    log.warning("Do not schedule blocking work!")
                    time.sleep(seconds)
                    diff = item.duetime - self.scheduler.now()

                if not item.is_cancelled():
                    item.invoke()

class CurrentThreadScheduler(Scheduler):
    """Represents an object that schedules units of work on the current
    thread. You never want to schedule timeouts using the CurrentThreadScheduler
    since it will block the current thread while waiting."""

    def __init__(self):
        """Gets a scheduler that schedules work as soon as possible on the
        current thread."""

        self.queue = None

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        log.debug("CurrentThreadScheduler.schedule(state=%s)", state)
        return self.schedule_relative(timedelta(0), action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_timedelta(duetime)

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
        """Schedules an action to be executed at duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now(), action, state=None)

    def schedule_required(self):
        """Gets a value indicating whether the caller must call a schedule 
        method. If the trampoline is active, then it returns False; otherwise, 
        if  the trampoline is not active, then it returns True."""
        
        return self.queue is None

    def ensure_trampoline(self, action):
        """Method for testing the CurrentThreadScheduler"""

        if self.queue is None:
            return self.schedule(action)
        else:
            return action(self, None)

Scheduler.current_thread = current_thread_scheduler = CurrentThreadScheduler()