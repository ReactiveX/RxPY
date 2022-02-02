from threading import RLock
from typing import Any

from rx.core.abc import DisposableBase, SchedulerBase


class ScheduledDisposable(DisposableBase):
    """Represents a disposable resource whose disposal invocation will
    be scheduled on the specified Scheduler"""

    def __init__(self, scheduler: SchedulerBase, disposable: DisposableBase) -> None:
        """Initializes a new instance of the ScheduledDisposable class
        that uses a Scheduler on which to dispose the disposable."""

        self.scheduler = scheduler
        self.disposable = disposable
        self.is_disposed = False
        self.lock = RLock()

        super().__init__()

    def dispose(self) -> None:
        """Disposes the wrapped disposable on the provided scheduler."""

        parent = self

        def action(scheduler: SchedulerBase, state: Any):
            """Scheduled dispose action"""

            should_dispose = False

            with self.lock:
                if not parent.is_disposed:
                    parent.is_disposed = True
                    should_dispose = True
            if should_dispose:
                parent.disposable.dispose()

        self.scheduler.schedule(action)
