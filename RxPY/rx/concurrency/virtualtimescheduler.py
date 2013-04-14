import logging

from rx.internal import PriorityQueue, ArgumentOutOfRangeException

from .scheduler import Scheduler
from .scheduleditem import ScheduledItem
from .scheduleperiodicrecursive import SchedulePeriodicRecursive

log = logging.getLogger("Rx")

class VirtualTimeScheduler(Scheduler):
    """Virtual Scheduler"""
    def __init__(self, initial_clock=0, comparer=None):
        """Creates a new virtual time scheduler with the specified initial 
        clock value and absolute time comparer.
        
        Keyword arguments:
        initial_clock -- Initial value for the clock.
        comparer -- Comparer to determine causality of events based on absolute time.
        """
        
        self.clock = initial_clock
        self.comparer = comparer
        self.is_enabled = False
        self.queue = PriorityQueue(1024)
        
    def local_now(self):
        return self.to_datetime_offset(self.clock)

    def schedule(self, action, state=None):
        return self.schedule_absolute(self.clock, action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at dueTime. Return the disposable
        object used to cancel the scheduled action (best effort)

        Keyword arguments:
        due_time -- Relative time after which to execute the action.
        action -- Action to be executed.
        state -- [Optional] State passed to the action to be executed.
        """
        log.debug("VirtualTimeScheduler.schedule_relative(duetime=%s, state=%s)" % (duetime, state))

        runat = self.add(self.clock, self.to_relative(duetime))
        return self.schedule_absolute(runat, action, state)

    def schedule_absolute(self, duetime, action, state=None):
        log.debug("VirtualTimeScheduler.schedule_absolute(duetime=%s, state=%s)" % (duetime, state))
        
        def run(scheduler, state1):
            #print ("VirtualTimeScheduler:schedule_absolute:run(%s)" % repr(state1))
            self.queue.remove(si)
            
            #print ("running action", action.__doc__)
            return action(scheduler, state1)
        
        si = ScheduledItem(self, state, run, duetime, self.comparer)
        self.queue.enqueue(si)
        return si.disposable
    
    def schedule_periodic(self, period, action, state=None):
        scheduler = SchedulePeriodicRecursive(self, period, action, state)
        return scheduler.start()
        
    def start(self):
        """Starts the virtual time scheduler."""
        next = None
        if not self.is_enabled:
            self.is_enabled = True
            while self.is_enabled:
                #print (self.clock)
                next = self.get_next()
                if next:
                    if self.comparer(next.duetime, self.clock) > 0:
                        self.clock = next.duetime
                        log.info("VirtualTimeScheduler.start(), clock: %s" % self.clock)
                    #else:
                    #    print ("skipping", next.duetime, self.clock)
                    
                    #print ("Invoke: ", self.clock, next.action)
                    next.invoke()
                else:
                    self.is_enabled = False
    
    def stop(self):
        """Stops the virtual time scheduler."""
        self.is_enabled = False
    
    def advance_to(self, time):
        """Advances the scheduler's clock to the specified time, running all 
        work till that point.
        
        Keyword arguments:
        time -- Absolute time to advance the scheduler's clock to.
        """
        print ("advance_to()")
        next = None
        if self.comparer(self.clock, time) >= 0:
            raise ArgumentOutOfRangeException()
        
        if not self.is_enabled:
            self.is_enabled = True
            while self.is_enabled:
                next = self.get_next()
                if next and self.comparer(next.duetime, time) <= 0:
                    if self.comparer(next.dueTime, self.clock) > 0:
                        self.clock = next.duetime

                    next.invoke()
                else:
                    self.is_enabled = False
            
            self.clock = time
        
    def advance_by(self, time):
        """Advances the scheduler's clock by the specified relative time, 
        running all work scheduled for that timespan.
        
        Keyword arguments:
        time -- Relative time to advance the scheduler's clock by.
        """
        log.debug("VirtualTimeScheduler.advance_by(time=%s)" % time)

        dt = self.add(self.clock, time)
        if self.comparer(self.clock, dt) >= 0:
            raise ArgumentOutOfRangeException()
        
        return self.advance_to(dt)
    
    def sleep(self, time):
        """Advances the scheduler's clock by the specified relative time.

        Keyword arguments:
        time -- Relative time to advance the scheduler's clock by.
        """
        dt = self.add(self.clock, time)

        if self.comparer(self.clock, dt) >= 0:
            raise ArgumentOutOfRangeException()

        self.clock = dt

    def get_next(self):
        """Returns the next scheduled item to be executed."""
        while self.queue.length > 0:
            next = self.queue.peek()
            if next.is_cancelled():
                self.queue.dequeue()
            else:
                return next
        
        return None
