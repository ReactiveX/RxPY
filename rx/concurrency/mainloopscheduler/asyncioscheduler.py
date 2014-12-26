# Same example as autocomplete.py but instead using the asyncio mainloop
# and the AsyncIOScheduler

import logging
from datetime import datetime, timedelta
asyncio = None

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.concurrency.scheduler import Scheduler

log = logging.getLogger("Rx")

class AsyncIOScheduler(Scheduler):
    """A scheduler that schedules work via the asyncio mainloop."""

    def __init__(self, loop=None):
        global asyncio
        import asyncio
        self.loop = loop or asyncio.get_event_loop()

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        scheduler = self
        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)

        handle = [self.loop.call_soon(interval)]

        def dispose():
            # nonlocal handle
            handle[0].cancel()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = self.to_relative(duetime)/1000.0
        if seconds == 0:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)

        handle = [self.loop.call_later(seconds, interval)]

        def dispose():
            # nonlocal handle
            handle[0].cancel()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        :param datetime duetime: Absolute time after which to execute the
            action.
        :param types.FunctionType action: Action to be executed.
        :param T state: Optional state to be given to the action function.

        :returns: The disposable object used to cancel the scheduled action
            (best effort).
        :rtype: Disposable
        """

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now(), action, state)

    def now(self):
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.
        """
        
        return self.to_datetime(self.loop.time())
