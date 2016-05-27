import logging
from concurrent.futures import ThreadPoolExecutor

from rx.core import Scheduler, Disposable
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable

from .timeoutscheduler import TimeoutScheduler

log = logging.getLogger("Rx")


class ThreadPoolScheduler(TimeoutScheduler):
    """A scheduler that schedules work via the thread pool and threading
    timers."""

    def __init__(self, max_workers=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        disposable = SingleAssignmentDisposable()

        def run():
            disposable.disposable = self.invoke_action(action, state)
        future = self.executor.submit(run)

        def dispose():
            future.cancel()
        return CompositeDisposable(disposable, Disposable.create(dispose))

Scheduler.thread_pool = thread_pool_scheduler = ThreadPoolScheduler()
