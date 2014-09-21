from .disposable import Disposable

class ScheduledDisposable(Disposable):
    def __init__(self, scheduler, disposable):
        self.scheduler = scheduler
        self.disposable = disposable
        super(ScheduledDisposable, self).__init__()
        
    def dispose(self):
        parent = self

        def action(scheduler, state):
            should_dispose = False
            with self.lock:
                if not parent.is_disposed:
                    parent.is_disposed = True
                    should_dispose = True
            parent.disposable.dispose()

        self.scheduler.schedule(action)
