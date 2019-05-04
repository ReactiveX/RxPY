import logging
import asyncio

from concurrent.futures import Future
from datetime import datetime
from typing import Optional

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from ..schedulerbase import SchedulerBase


log = logging.getLogger("Rx")


class AsyncIOScheduler(SchedulerBase):
    """A scheduler that schedules work via the asyncio mainloop."""

    def __init__(self,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 threadsafe: bool = False
                 ) -> None:
        super().__init__()
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.threadsafe: bool = threadsafe

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
        if self.threadsafe is False:
            return self._schedule(action, state=state)

        return self._schedule_threadsafe(action, state=state)

    def _schedule(self,
                  action: typing.ScheduledAction,
                  state: Optional[typing.TState] = None
                  ) -> typing.Disposable:
        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        handle = self.loop.call_soon(interval)

        def dispose() -> None:
            handle.cancel()

        return CompositeDisposable(sad, Disposable(dispose))

    def _schedule_threadsafe(self,
                             action: typing.ScheduledAction,
                             state: Optional[typing.TState] = None
                             ) -> typing.Disposable:
        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        handle = self.loop.call_soon_threadsafe(interval)

        def dispose() -> None:
            future = Future()

            def cancel_handle() -> None:
                handle.cancel()
                future.set_result(0)

            self.loop.call_soon_threadsafe(cancel_handle)
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
        if self.threadsafe is False:
            return self._schedule_relative(duetime, action, state=state)
        else:
            return self._schedule_relative_threadsafe(duetime, action, state=state)

    def _schedule_relative(self,
                           duetime: typing.RelativeTime,
                           action: typing.ScheduledAction,
                           state: Optional[typing.TState] = None
                           ) -> typing.Disposable:
        seconds = self.to_seconds(duetime)
        if seconds == 0:
            return self.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        handle = self.loop.call_later(seconds, interval)

        def dispose() -> None:
            handle.cancel()

        return CompositeDisposable(sad, Disposable(dispose))

    def _schedule_relative_threadsafe(self,
                                      duetime: typing.RelativeTime,
                                      action: typing.ScheduledAction,
                                      state: Optional[typing.TState] = None
                                      ) -> typing.Disposable:
        seconds = self.to_seconds(duetime)
        if seconds == 0:
            return self.schedule(action, state=state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        # the operations on the list used here are atomic, so there is no
        # need to protect its access with a lock
        handle = []

        def stage2() -> None:
            handle.append(self.loop.call_later(seconds, interval))

        handle.append(self.loop.call_soon_threadsafe(stage2))

        def dispose() -> None:
            future = Future()

            def cancel_handle() -> None:
                try:
                    handle.pop().cancel()
                    handle.pop().cancel()
                except Exception:
                    pass
                future.set_result(0)

            self.loop.call_soon_threadsafe(cancel_handle)
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

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self.to_datetime(self.loop.time())
