from concurrent.futures import ThreadPoolExecutor

from .newthreadscheduler import NewThreadScheduler


class ThreadPoolScheduler(NewThreadScheduler):
    """A scheduler that schedules work via the thread pool."""

    class ThreadPoolThread:
        """Wraps a concurrent future as a thread."""

        def __init__(self, executor, run):
            self.run = run
            self.future = None
            self.executor = executor

        def start(self):
            self.future = self.executor.submit(self.run)

        def cancel(self):
            self.future.cancel()

    def __init__(self, max_workers=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        def thread_factory(target, *args):
            return self.ThreadPoolThread(self.executor, target)

        super().__init__(thread_factory)

