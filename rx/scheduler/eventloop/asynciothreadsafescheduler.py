import logging
import asyncio

from concurrent.futures import Future
from typing import List, Optional

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from .asyncioscheduler import AsyncIOScheduler


log = logging.getLogger("Rx")


class AsyncIOThreadSafeScheduler(AsyncIOScheduler):
    """A scheduler that schedules work via the asyncio mainloop. This is a
    subclass of AsyncIOScheduler which uses the threadsafe asyncio methods.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        """Create a new AsyncIOThreadSafeScheduler.

        Args:
            loop: Instance of asyncio event loop to use; typically, you would
                get this by asyncio.get_event_loop()
        """

        super().__init__(loop)

    def schedule(self,
                 action: typing.ScheduledAction,
                 state: Optional[typing.TState] = None
                 ) -> typing.Disposable:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        handle = self._loop.call_soon_threadsafe(interval)

        def dispose() -> None:
            future: Future = Future()

            def cancel_handle() -> None:
                handle.cancel()
                future.set_result(0)

            self._loop.call_soon_threadsafe(cancel_handle)
            future.result()

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule_relative(self,
                          duetime: typing.RelativeTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        seconds = self.to_seconds(duetime)
        if seconds <= 0:
            return self.schedule(action, state=state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        # the operations on the list used here are atomic, so there is no
        # need to protect its access with a lock
        handle: List[asyncio.Handle] = []

        def stage2() -> None:
            handle.append(self._loop.call_later(seconds, interval))

        handle.append(self._loop.call_soon_threadsafe(stage2))

        def dispose() -> None:
            future: Future = Future()

            def cancel_handle() -> None:
                try:
                    handle.pop().cancel()
                    handle.pop().cancel()
                except Exception:
                    pass
                future.set_result(0)

            self._loop.call_soon_threadsafe(cancel_handle)
            future.result()

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule_absolute(self,
                          duetime: typing.AbsoluteTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state=state)
