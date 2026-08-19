import heapq
import logging
import threading
from collections.abc import MutableMapping
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar
from weakref import WeakKeyDictionary

from reactivex import abc, typing
from reactivex.disposable import Disposable
from reactivex.internal.concurrency import default_thread_factory
from reactivex.internal.constants import DELTA_ZERO
from reactivex.internal.priorityqueue import PriorityQueue

from .periodicscheduler import PeriodicScheduler
from .scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

_TState = TypeVar("_TState")


class TimeoutScheduler(PeriodicScheduler):
    """A scheduler that schedules work via timed callbacks.

    Uses a single dedicated timer thread to track due times and dispatches
    each fired action onto a thread pool for execution. This avoids spawning
    one OS thread per pending timeout while keeping user callbacks off the
    timer thread (so nested or blocking handlers cannot deadlock other
    timeouts). Cancellation removes the item from the timer queue promptly.

    Prefer :meth:`singleton` (also used by ``TimeoutScheduler()``). Disposing
    the process-wide singleton is unsupported and will break subsequent
    timeout-based operators.
    """

    _lock = threading.Lock()
    _global: MutableMapping[type, "TimeoutScheduler"] = WeakKeyDictionary()

    _thread_factory: typing.StartableFactory
    _thread: typing.Startable | None
    _condition: threading.Condition
    _queue: PriorityQueue[ScheduledItem]
    _executor: ThreadPoolExecutor

    @classmethod
    def singleton(cls) -> "TimeoutScheduler":
        with TimeoutScheduler._lock:
            try:
                self = TimeoutScheduler._global[cls]
            except KeyError:
                self = super().__new__(cls)
                PeriodicScheduler.__init__(self)
                self._thread_factory = default_thread_factory
                self._thread = None
                self._condition = threading.Condition(threading.Lock())
                self._queue = PriorityQueue()
                self._executor = ThreadPoolExecutor(
                    thread_name_prefix=f"{cls.__name__}-worker"
                )
                TimeoutScheduler._global[cls] = self
        return self

    def __new__(cls) -> "TimeoutScheduler":
        return cls.singleton()

    def schedule(
        self, action: abc.ScheduledAction[_TState], state: _TState | None = None
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
        action: abc.ScheduledAction[_TState],
        state: _TState | None = None,
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
        return self.schedule_absolute(self.now + duetime, action, state=state)

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: abc.ScheduledAction[_TState],
        state: _TState | None = None,
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
        si: ScheduledItem = ScheduledItem(self, state, action, dt)

        with self._condition:
            self._queue.enqueue(si)
            self._condition.notify()
            self._ensure_thread()

        return Disposable(lambda: self._cancel(si))

    def _cancel(self, item: ScheduledItem) -> None:
        with self._condition:
            was_head = bool(self._queue) and self._queue.peek() is item
            item.cancel()
            self._remove_by_identity(item)
            if was_head:
                self._condition.notify()

    def _remove_by_identity(self, item: ScheduledItem) -> bool:
        """Remove *item* from the queue by identity.

        :meth:`PriorityQueue.remove` uses ``==``, and
        :class:`ScheduledItem` equality is due-time only, which is unsafe
        when multiple timers share a due time.
        """

        for index, (queued, _) in enumerate(self._queue.items):
            if queued is item:
                self._queue.items.pop(index)
                heapq.heapify(self._queue.items)
                if not self._queue.items:
                    self._queue.count = PriorityQueue.MIN_COUNT
                return True
        return False

    def _ensure_thread(self) -> None:
        """Ensures there is a timer thread running. Call under the gate."""

        if not self._thread:
            thread = self._thread_factory(self._run)
            self._thread = thread
            thread.start()

    def _run(self) -> None:
        """Timer loop: wait for due items and dispatch them to the pool."""

        while True:
            ready: list[ScheduledItem] = []

            with self._condition:
                while True:
                    if not self._queue:
                        self._thread = None
                        return

                    time = self.now
                    item = self._queue.peek()
                    seconds = (item.duetime - time).total_seconds()
                    if seconds > 0:
                        log.debug("timeout: %s", seconds)
                        self._condition.wait(seconds)
                        continue

                    while self._queue and self._queue.peek().duetime <= self.now:
                        ready.append(self._queue.dequeue())
                    break

            for item in ready:
                if not item.is_cancelled():
                    self._executor.submit(item.invoke)


__all__ = ["TimeoutScheduler"]
