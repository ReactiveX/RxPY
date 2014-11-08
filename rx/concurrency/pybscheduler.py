import pyb

from rx.internal import PriorityQueue
from rx.disposables import Disposable
from rx.concurrency.scheduler import Scheduler
from rx.concurrency.scheduleditem import ScheduledItem

class _PyboardScheduler(Scheduler):
    """A scheduler that schedules work via a pyboard mainloop that kicks it 
    regularly using the run() method. The scheduler uses the pyboard timers
    to signlal the mainloop for wakeup so WFI instructions may be used."""

    def __init__(self, timer=None):
        """Gets a scheduler that schedules work on the pyboard."""

        DEFAULT_TIMER = 4

        self.queue = PriorityQueue()
        self.timer = pyb.Timer(timer or DEFAULT_TIMER)
        #self.fired = False

    def __call__(self):
        """Simple singleton handling"""
        return self

    def run(self):
        while self.queue.length:
            item = self.queue.peek()
            diff = item.duetime - self.now()
            if diff > 0:
                #print("msecs=%d" % diff)
                self.start_timer(1000/diff)
                break

            item = self.queue.dequeue()
            #print("dequeue")
            if not item.is_cancelled():
                #print("invoke()")
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

        #print("schedule_relative(duetime=%s, action=%s, state=%s)" % (duetime, repr(action), state))
        dt = self.now() + Scheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)

        self.queue.enqueue(si)
        return si.disposable

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime."""

        return self.schedule_relative(duetime - self.now(), action, state=None)

    def schedule_periodic(self, period, action, state=None):
        """Schedules a periodic piece of work by dynamically discovering the
        scheduler's capabilities.

        Keyword arguments:
        period -- Period for running the work periodically.
        action -- Action to be executed.
        state -- [Optional] Initial state passed to the action upon the first
            iteration.

        Returns the disposable object used to cancel the scheduled recurring
        action (best effort)."""

        timer = [None]
        s = [state]

        def interval(scheduler, state=None):
            new_state = action(s[0])
            if not new_state is None: # Update state if other than None
                s[0] = new_state

            timer[0] = self.schedule_relative(period, interval)
        timer[0] = self.schedule_relative(period, interval)
        
        def dispose():
            timer[0].dispose()

        return Disposable(dispose)

    def now(self):
        return pyb.millis()

# Singleton. There shall be only one
PyboardScheduler = _PyboardScheduler()
Scheduler.pyboard = pyboard_scheduler = PyboardScheduler()