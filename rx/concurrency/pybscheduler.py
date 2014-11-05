import pyb

from rx.internal import PriorityQueue
from rx.concurrency.scheduler import Scheduler
from rx.concurrency.scheduleditem import ScheduledItem

class PybScheduler(Scheduler):
    """A scheduler that schedules work via the pyboard Timers."""

    def __init__(self):
        """Gets a scheduler that schedules work on the pyboard."""

        self.queue = PriorityQueue()
        self.timer = pyb.Timer(4)
        #self.fired = False

    def run(self):
        while self.queue.length:
            item = self.queue.peek()
            diff = item.duetime - self.now()
            if diff > 0:
                print("msecs=%d" % diff)
                self.start_timer(1000/diff)
                break

            item = self.queue.dequeue()
            print("dequeue")
            if not item.is_cancelled():
                print("invoke()")
                item.invoke()
        else:
            self.stop_timer()

    def start_timer(self, hz):
        #print("set_timer(%s)" % hz)
        self.timer.init(freq=hz)
        
        def cb(t):
            pass
            #self.fired = True
        self.timer.callback(cb)
        
    def stop_timer(self):
        self.timer.callback(None)
        self.timer.deinit()

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        return self.schedule_relative(0, action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        print("schedule_relative(duetime=%s, action=%s, state=%s)" % (duetime, repr(action), state))
        dt = self.now() + Scheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)

        self.queue.enqueue(si)
        return si.disposable

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime."""

        return self.schedule_relative(duetime - self.now(), action, state=None)

    def schedule_required(self):
        """Gets a value indicating whether the caller must call a schedule 
        method. If the trampoline is active, then it returns False; otherwise, 
        if  the trampoline is not active, then it returns True."""
        
        return self.queue is None

    def ensure_trampoline(self, action):
        """Method for testing the Scheduler"""

        if self.queue is None:
            return self.schedule(action)
        else:
            return action(self, None)

    def now(self):
        return pyb.millis()
