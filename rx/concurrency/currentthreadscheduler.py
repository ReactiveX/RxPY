# Current Thread Scheduler

from datetime import timedelta
from Queue import PriorityQueue

import scheduler
from scheduler import Scheduler
from scheduleditem import ScheduledItem

class Trampoline(object):
    def __init__(self):
        self.queue = PriorityQueue(4)

    def enqueue(self, item):
        #print "Trampoline:enqueue"
        return self.queue.put(item)

    def dispose(self):
        self.queue = None

    def run(self):
        #print "Trampoline:run"
        while self.queue.qsize() > 0:
            item = self.queue.get();
            if not item.is_cancelled():
                while item.duetime - Scheduler.now() > timedelta(0):
                    pass

                if not item.is_cancelled():
                    #print "item.invoke"
                    item.invoke()

class CurrentThreadScheduler(Scheduler):    
    def __init__(self):
        self.queue = None

    def schedule(self, action, state=None):
        #print "CurrentThreadScheduler:schedule"
        return self.schedule_relative(0, action, state)

    def schedule_relative(self, duetime, action, state=None):
        dt = self.now() + Scheduler.normalize(duetime)
        si = ScheduledItem(self, state, action, dt)
        
        if not self.queue:
            self.queue = Trampoline()
            try:
                self.queue.enqueue(si)
                self.queue.run()
            finally:
                self.queue.dispose()
            
        else:
            self.queue.enqueue(si)
        
        return si.disposable

    def schedule_absolute(self, duetime, action, state=None):
        return self.schedule_relative(duetime - self.now(), action, state=None)

    #var currentScheduler = new Scheduler(defaultNow, scheduleNow, scheduleRelative, scheduleAbsolute)
    
    def schedule_required(self):
        return queue == null
    
    def ensure_trampoline(self, action):
        if self.queue is None:
            return this.schedule(action)
        else:
            return action()
