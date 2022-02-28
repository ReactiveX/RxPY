import logging
import threading
from collections import deque
from typing import Deque, Optional, TypeVar

from reactivex import abc, typing
from reactivex.disposable import Disposable
from reactivex.internal.concurrency import default_thread_factory
from reactivex.internal.constants import DELTA_ZERO
from reactivex.internal.exceptions import DisposedException
from reactivex.internal.priorityqueue import PriorityQueue

from .periodicscheduler import PeriodicScheduler
from .scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

_TState = TypeVar("_TState")


class EventLoopScheduler(PeriodicScheduler, abc.DisposableBase):
    """Creates an object that schedules units of work on a designated thread."""

    def __init__(
        self,
        thread_factory: Optional[typing.StartableFactory] = None,
        exit_if_empty: bool = False,
    ) -> None:
        super().__init__()
        self._is_disposed = False

        self._thread_factory: typing.StartableFactory = (
            thread_factory or default_thread_factory
        )
        self._thread: Optional[typing.Startable] = None
        self._condition = threading.Condition(threading.Lock())
        self._queue: PriorityQueue[ScheduledItem] = PriorityQueue()
        self._ready_list: Deque[ScheduledItem] = deque()

        self._exit_if_empty = exit_if_empty

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

        return self.schedule_absolute(self.now, action, state=state)

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

        duetime = max(DELTA_ZERO, self.to_timedelta(duetime))
        return self.schedule_absolute(self.now + duetime, action, state)

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

        if self._is_disposed:
            raise DisposedException()

        dt = self.to_datetime(duetime)
        si: ScheduledItem = ScheduledItem(self, state, action, dt)

        with self._condition:
            if dt <= self.now:
                self._ready_list.append(si)
            else:
                self._queue.enqueue(si)
            self._condition.notify()  # signal that a new item is available
            self._ensure_thread()

        return Disposable(si.cancel)

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

        if self._is_disposed:
            raise DisposedException()

        return super().schedule_periodic(period, action, state=state)

    def _has_thread(self) -> bool:
        """Checks if there is an event loop thread running."""
        with self._condition:
            return not self._is_disposed and self._thread is not None

    def _ensure_thread(self) -> None:
        """Ensures there is an event loop thread running. Should be
        called under the gate."""

        if not self._thread:
            thread = self._thread_factory(self.run)
            self._thread = thread
            thread.start()

    def run(self) -> None:
        """Event loop scheduled on the designated event loop thread.
        The loop is suspended/resumed using the condition which gets notified
        by calls to Schedule or calls to dispose."""

        ready: Deque[ScheduledItem] = deque()

        while True:

            with self._condition:

                # The notification could be because of a call to dispose. This
                # takes precedence over everything else: We'll exit the loop
                # immediately. Subsequent calls to Schedule won't ever create a
                # new thread.
                if self._is_disposed:
                    return

                # Sort the ready_list (from recent calls for immediate schedule)
                # and the due subset of previously queued items.
                time = self.now
                while self._queue:
                    due = self._queue.peek().duetime
                    while self._ready_list and due > self._ready_list[0].duetime:
                        ready.append(self._ready_list.popleft())
                    if due > time:
                        break
                    ready.append(self._queue.dequeue())
                while self._ready_list:
                    ready.append(self._ready_list.popleft())

            # Execute the gathered actions
            while ready:
                item = ready.popleft()
                if not item.is_cancelled():
                    item.invoke()

            # Wait for next cycle, or if we're done let's exit if so configured
            with self._condition:

                if self._ready_list:
                    continue

                elif self._queue:
                    time = self.now
                    item = self._queue.peek()
                    seconds = (item.duetime - time).total_seconds()
                    if seconds > 0:
                        log.debug("timeout: %s", seconds)
                        self._condition.wait(seconds)

                elif self._exit_if_empty:
                    self._thread = None
                    return

                else:
                    self._condition.wait()

    def dispose(self) -> None:
        """Ends the thread associated with this scheduler. All
        remaining work in the scheduler queue is abandoned.
        """

        with self._condition:
            if not self._is_disposed:
                self._is_disposed = True
                self._condition.notify()
