import logging
import threading
from collections import deque
from typing import Any, Deque, Optional

from rx.disposable import Disposable
from rx.core import typing
from rx.internal.concurrency import default_thread_factory
from rx.internal.exceptions import DisposedException
from rx.internal.priorityqueue import PriorityQueue

from .schedulerbase import SchedulerBase
from .scheduleditem import ScheduledItem

log = logging.getLogger('Rx')


class EventLoopScheduler(SchedulerBase, typing.Disposable):
    """Creates an object that schedules units of work on a designated
    thread."""

    def __init__(self, thread_factory: Optional[typing.StartableFactory] = None,
                 exit_if_empty: bool = False) -> None:
        super(EventLoopScheduler, self).__init__()
        self._is_disposed = False

        self._thread_factory = thread_factory or default_thread_factory
        self._thread: Optional[threading.Thread] = None
        self._condition = threading.Condition(threading.Lock())
        self._queue: PriorityQueue[ScheduledItem[typing.TState]] = PriorityQueue()
        self._ready_list: Deque[ScheduledItem] = deque()

        self._exit_if_empty = exit_if_empty

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        return self.schedule_absolute(self.now, action, state=state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime."""

        duetime = SchedulerBase.normalize(self.to_timedelta(duetime))
        return self.schedule_absolute(self.now + duetime, action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime."""

        if self._is_disposed:
            raise DisposedException()

        dt = self.to_datetime(duetime)
        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, dt)

        with self._condition:
            if dt <= self.now:
                self._ready_list.append(si)
            else:
                self._queue.enqueue(si)
            self._condition.notify()  # signal that a new item is available
            self._ensure_thread()

        return Disposable(si.cancel)

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledPeriodicAction, state: Any = None
                         ) -> typing.Disposable:
        """Schedule a periodic piece of work."""

        if self._is_disposed:
            raise DisposedException()

        disposed: bool = False
        s = state

        def invoke_periodic(scheduler, state):
            if disposed:
                return

            if period:
                self.schedule_relative(period, invoke_periodic)

            nonlocal s
            new_state = action(s)
            if new_state is not None:
                s = new_state

        self.schedule_relative(period, invoke_periodic)

        def dispose():
            nonlocal disposed
            disposed = True

        return Disposable(dispose)

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
                    if due > time:
                        break
                    while self._ready_list and due > self._ready_list[0].duetime:
                        ready.append(self._ready_list.popleft())
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
                    due = self._queue.peek().duetime - self.now
                    seconds = due.total_seconds()
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


event_loop_scheduler = EventLoopScheduler()
