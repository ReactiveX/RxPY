import logging
from datetime import datetime, timedelta

pygame = None

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.internal import PriorityQueue
from rx.concurrency.scheduler import Scheduler
from rx.concurrency.scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

class PyGameScheduler(Scheduler):
    """A scheduler that schedules works for PyGame.

    http://www.pygame.org/docs/ref/time.html
    http://www.pygame.org/docs/ref/event.html   
    """

    def __init__(self, event_id=None):
        global pygame
        import pygame
        
        self.timer = None
        self.event_id = event_id or pygame.USEREVENT
        
        self.queue = PriorityQueue()
        
    def schedule(self, action, state=None):
        log.debug("PyGameScheduler.schedule(state=%s)", state)
        return self.schedule_relative(0, action, state)
 
    def run(self):
        while self.queue.length:
            item = self.queue.peek()
            diff = item.duetime - self.now()
            if diff > 0:
                break
            
            item = self.queue.dequeue()
            if not item.is_cancelled():
                item.invoke()

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        #log.debug("PyGameScheduler.schedule_relative(duetime=%s, state=%s)" % (duetime, state))
        
        dt = self.now() + PyGameScheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)

        self.queue.enqueue(si)

        return si.disposable

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        return self.schedule_relative(duetime - self.now(), action, state)

    def default_now(self):
        return pygame.time.get_ticks()

    @classmethod
    def to_relative(cls, timespan):
        """Converts timespan to from datetime/timedelta to milliseconds"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.fromtimestamp(0)
        if isinstance(timespan, timedelta):
            timespan = int(timespan.total_seconds()*1000)

        print(timespan)
        return timespan

    @classmethod
    def normalize(cls, timespan):
        """PyGame operates with milliseconds"""
        nospan = 0

        msecs = 0
        if isinstance(timespan, timedelta):
            msecs = timespan.seconds+timespan.microseconds/1000.0

        elif isinstance(timespan, datetime):
            msecs = timespan.totimestamp()*1000
        else:
            msecs = timespan

        if not timespan or timespan < nospan:
            msecs = nospan

        return msecs


