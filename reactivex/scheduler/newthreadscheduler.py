import logging
import threading
from datetime import datetime
from typing import Optional, TypeVar

from reactivex import abc, typing
from reactivex.disposable import Disposable
from reactivex.internal.concurrency import default_thread_factory

from .eventloopscheduler import EventLoopScheduler
from .periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")

log = logging.getLogger("Rx")


class NewThreadScheduler(PeriodicScheduler):
    """Creates an object that schedules each unit of work on a separate thread."""

    def __init__(
        self, thread_factory: Optional[typing.StartableFactory] = None
    ) -> None:
        super().__init__()
        self.thread_factory: typing.StartableFactory = (
            thread_factory or default_thread_factory
        )

    def schedule(
        self, action: typing.ScheduledAction[_TState], state: Optional[_TState] = None
    ) -> abc.DisposableBase:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        scheduler = EventLoopScheduler(
            thread_factory=self.thread_factory, exit_if_empty=True
        )
        return scheduler.schedule(action, state)

    def schedule_relative(
        self,
        duetime: typing.RelativeTime,
        action: typing.ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        scheduler = EventLoopScheduler(
            thread_factory=self.thread_factory, exit_if_empty=True
        )
        return scheduler.schedule_relative(duetime, action, state)

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: typing.ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        dt = self.to_datetime(duetime)
        return self.schedule_relative(dt - self.now, action, state=state)

    def schedule_periodic(
        self,
        period: typing.RelativeTime,
        action: typing.ScheduledPeriodicAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules a periodic piece of work.

        Args:
            period: Period in seconds or timedelta for running the
                work periodically.
            action: Action to be executed.
            state: [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort).
        """

        seconds: float = self.to_seconds(period)
        timeout: float = seconds
        disposed: threading.Event = threading.Event()

        def run() -> None:
            nonlocal state, timeout
            while True:
                if timeout > 0.0:
                    disposed.wait(timeout)
                if disposed.is_set():
                    return

                time: datetime = self.now

                state = action(state)

                timeout = seconds - (self.now - time).total_seconds()

        thread = self.thread_factory(run)
        thread.start()

        def dispose() -> None:
            disposed.set()

        return Disposable(dispose)
