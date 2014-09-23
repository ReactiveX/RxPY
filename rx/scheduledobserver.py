from rx.abstractobserver import AbstractObserver
from rx.disposables import SerialDisposable

class ScheduledObserver(AbstractObserver):
    def __init__(self, scheduler, observer):
        super(ScheduledObserver, self).__init__()
        self.scheduler = scheduler
        self.observer = observer
        self.is_acquired = False
        self.has_faulted = False
        self.queue = []
        self.disposable = SerialDisposable()

    def next(self, value):
        def func():
            self.observer.on_next(value)
        self.queue.append(func)

    def error(self, exception):
        def func():
            self.observer.on_error(exception)
        self.queue.append(func)

    def completed(self):
        def func():
            self.observer.on_completed()
        self.queue.append(func)

    def ensure_active(self):
        is_owner, parent = False, self
        if not self.has_faulted and len(self.queue):
            is_owner = not self.is_acquired
            self.is_acquired = True

        if is_owner:
            def action(action1, state):
                work = None
                if len(parent.queue):
                    work = parent.queue.pop(0)
                else:
                    parent.is_acquired = False
                    return

                try:
                    work()
                except Exception as ex:
                    parent.queue = []
                    parent.has_faulted = True
                    raise ex

                action1()
            self.disposable.disposable = self.scheduler.schedule_recursive(action)

    def dispose(self):
        super(ScheduledObserver, self).dispose()
        self.disposable.dispose()
