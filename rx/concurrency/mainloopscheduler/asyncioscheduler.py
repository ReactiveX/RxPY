import logging
import asyncio
from datetime import datetime
from concurrent.futures import Future

from rx import disposable
from rx.core import typing
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

log = logging.getLogger("Rx")


class AsyncIOScheduler(SchedulerBase):
    """A scheduler that schedules work via the asyncio mainloop."""

    def __init__(self, loop=None, threadsafe=False):
        self.loop = loop or asyncio.get_event_loop()
        self.threadsafe = threadsafe

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""
        if self.threadsafe is False:
            return self._schedule(action, state)

        return self._schedule_threadsafe(action, state)

    def _schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)
        handle = self.loop.call_soon(interval)

        def dispose():
            handle.cancel()

        return CompositeDisposable(sad, disposable.create(dispose))

    def _schedule_threadsafe(self, action, state=None):
        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        handle = self.loop.call_soon_threadsafe(interval)

        def dispose():
            future = Future()

            def cancel_handle():
                handle.cancel()
                future.set_result(0)

            self.loop.call_soon_threadsafe(cancel_handle)
            future.result()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Relative time after which to execute the
                action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        if self.threadsafe is False:
            return self._schedule_relative(duetime, action, state)
        else:
            return self._schedule_relative_threadsafe(duetime, action, state)

    def _schedule_relative(self, duetime, action, state=None):
        scheduler = self
        seconds = self.to_seconds(duetime)
        if seconds == 0:
            return scheduler.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        handle = self.loop.call_later(seconds, interval)

        def dispose():
            handle.cancel()

        return CompositeDisposable(sad, disposable.create(dispose))

    def _schedule_relative_threadsafe(self, duetime, action, state=None):
        scheduler = self
        seconds = self.to_seconds(duetime)
        if seconds == 0:
            return scheduler.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        # the operations on the list used here are atomic, so there is no
        # need to protect its access with a lock
        handle = []

        def stage2():
            handle.append(self.loop.call_later(seconds, interval))

        handle.append(self.loop.call_soon_threadsafe(stage2))

        def dispose():
            future = Future()

            def cancel_handle():
                try:
                    handle.pop().cancel()
                    handle.pop().cancel()
                except Exception:
                    pass
                future.set_result(0)

            self.loop.call_soon_threadsafe(cancel_handle)
            future.result()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time after which to execute the
            action.
            action: Action to be executed.
            state: Optional state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.
        """

        return self.to_datetime(self.loop.time()*1000)
