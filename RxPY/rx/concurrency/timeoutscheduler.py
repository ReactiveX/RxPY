from threading import Timer

from .scheduler import Scheduler

# Timeout Scheduler
class TimeoutScheduler(Scheduler):
    def __init__(self):
        self.timer = None

    def schedule_now(self, action, state=None):
        print("TimeoutScheduler:schedule_now()")
        scheduler = self
        disposable = SingleAssignmentDisposable()
        
        def interval():
            disposable.disposable = action(scheduler, state)

        def dispose():
            self.timer.cancel()
        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_relative(duetime, action, state=None):
        print("TimeoutScheduler:schedule_relative")
        scheduler = self
        dt = Scheduler.normalize(duetime);
        if dt == 0:
            return scheduler.schedule(action, state)
        
        disposable = SingleAssignmentDisposable()
        def interval():
            disposable.disposable = action(scheduler, state)
        
        seconds = dt.seconds
        self.timer = Timer(seconds, inteval)
        
        def dispose():
            self.timer.cancel()
        
        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_absolute(self, state, dueTime, action):
        print ("TimeoutScheduler:schedule_absolute")
        return this.schedule_relative(dueTime - this.now(), action, state)
