from .disposable import Disposable

class ScheduledDisposable(Disposable):
    def __init__(self, scheduler, disposable):
        self.scheduler = scheduler
        self.disposable = disposable
        self.is_disposed = False

    def dispose(self):
        parent = self
        def action(scheduler, state):
            if not parent.is_disposed:
                parent.is_disposed = True
                parent.disposable.dispose()

        self.scheduler.schedule(action)
