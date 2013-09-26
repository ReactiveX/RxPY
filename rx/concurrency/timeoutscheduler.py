import logging
from threading import Timer

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable

from .scheduler import Scheduler

log = logging.getLogger("Rx")

# Timeout Scheduler
class TimeoutScheduler(Scheduler):
    def __init__(self):
        self.timer = None

    def schedule(self, action, state=None):
        #print("TimeoutScheduler:schedule_now()")
        scheduler = self
        disposable = SingleAssignmentDisposable()
        
        def interval():
            #print ("TimeoutScheduler:schedule.interval()")
            disposable.disposable = action(scheduler, state)
        self.timer = Timer(0, interval)
        self.timer.start()
        def dispose():
            #print ("TimeoutScheduler:schedule.dispose()")
            self.timer.cancel()
        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        log.info("TimeoutScheduler:schedule_relative(%s)" % duetime)
        
        scheduler = self
        dt = Scheduler.normalize(duetime)
        if dt == 0:
            return scheduler.schedule(action, state)
        
        disposable = SingleAssignmentDisposable()
        def interval():
            log.info("TimeoutScheduler:schedule_relative.interval()")
            disposable.disposable = action(scheduler, state)
        
        seconds = dt.seconds+dt.microseconds/1000000
        log.info("timeout: %s" % seconds)
        self.timer = Timer(seconds, interval)
        self.timer.start()

        def dispose():
            log.debug("TimeoutScheduler:schedule_relative.dispose()")
            self.timer.cancel()
        
        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        #print ("TimeoutScheduler:schedule_absolute(%s)" % duetime)
        return self.schedule_relative(duetime - self.now(), action, state)

timeout_scheduler = TimeoutScheduler()