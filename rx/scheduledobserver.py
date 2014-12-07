from rx import Lock
from rx.abstractobserver import AbstractObserver
from rx.disposables import SerialDisposable

class ScheduledObserver(AbstractObserver):
    def __init__(self, scheduler, observer):
        super(ScheduledObserver, self).__init__(self._next, self._error, self._completed)

        self.scheduler = scheduler
        self.observer = observer

        self.lock = Lock()
        self.is_acquired = False
        self.has_faulted = False
        self.queue = []
        self.disposable = SerialDisposable()

        # Note to self: list append is thread safe
        # http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm

    def _next(self, value):
        def func():
            self.observer.on_next(value)
        self.queue.append(func)

    def _error(self, exception):
        def func():
            self.observer.on_error(exception)
        self.queue.append(func)

    def _completed(self):
        def func():
            self.observer.on_completed()
        self.queue.append(func)

    def ensure_active(self):
        is_owner = False

        with self.lock:
            if not self.has_faulted and len(self.queue):
                is_owner = not self.is_acquired
                self.is_acquired = True

        if is_owner:
            self.disposable.disposable = self.scheduler.schedule_recursive(self.run)

    def run(self, recurse, state):
        parent = self

        with self.lock:
            if len(parent.queue):
                work = parent.queue.pop(0)
            else:
                parent.is_acquired = False
                return

        try:
            work()
        except Exception as ex:
            with self.lock:
                parent.queue = []
                parent.has_faulted = True
            raise ex

        recurse()

    def dispose(self):
        super(ScheduledObserver, self).dispose()
        self.disposable.dispose()
