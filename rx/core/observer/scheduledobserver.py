import threading
from typing import List, Any

from rx.core import typing
from rx.disposable import SerialDisposable

from .observer import Observer


class ScheduledObserver(Observer):
    def __init__(self, scheduler: typing.Scheduler, observer: typing.Observer) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.observer = observer

        self.lock = threading.RLock()
        self.is_acquired = False
        self.has_faulted = False
        self.queue: List[typing.Action] = []
        self.disposable = SerialDisposable()

        # Note to self: list append is thread safe
        # http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm

    def _on_next_core(self, value: Any) -> None:
        def action():
            self.observer.on_next(value)
        self.queue.append(action)

    def _on_error_core(self, error: Exception) -> None:
        def action():
            self.observer.on_error(error)
        self.queue.append(action)

    def _on_completed_core(self) -> None:
        def action():
            self.observer.on_completed()
        self.queue.append(action)

    def ensure_active(self) -> None:
        is_owner = False

        with self.lock:
            if not self.has_faulted and self.queue:
                is_owner = not self.is_acquired
                self.is_acquired = True

        if is_owner:
            self.disposable.disposable = self.scheduler.schedule(self.run)

    def run(self, scheduler: typing.Scheduler, state: typing.TState) -> None:
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

        self.scheduler.schedule(self.run)

    def dispose(self) -> None:
        super().dispose()
        self.disposable.dispose()
