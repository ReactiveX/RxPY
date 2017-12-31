import threading
from rx.disposables import SerialDisposable

from .observerbase import ObserverBase


class ScheduledObserver(ObserverBase):
    def __init__(self, scheduler, observer):
        super().__init__()

        self.scheduler = scheduler
        self.observer = observer

        self.lock = threading.RLock()
        self.is_acquired = False
        self.has_faulted = False
        self.queue = []
        self.disposable = SerialDisposable()

        # Note to self: list append is thread safe
        # http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm

    def _send_core(self, value):
        def action():
            self.observer.send(value)
        self.queue.append(action)

    def _throw_core(self, error):
        def action():
            self.observer.throw(error)
        self.queue.append(action)

    def _close_core(self):
        def action():
            self.observer.close()
        self.queue.append(action)

    def ensure_active(self):
        is_owner = False

        with self.lock:
            if not self.has_faulted and self.queue:
                is_owner = not self.is_acquired
                self.is_acquired = True

        if is_owner:
            self.disposable.disposable = self.scheduler.schedule(self.run)

    def run(self, scheduler, state):
        parent = self

        with self.lock:
            if parent.queue:
                work = parent.queue.pop(0)
            else:
                parent.is_acquired = False
                return

        try:
            work()
        except Exception:
            with self.lock:
                parent.queue = []
                parent.has_faulted = True
            raise

        return self.scheduler.schedule(self.run)

    def dispose(self):
        super().dispose()
        self.disposable.dispose()
