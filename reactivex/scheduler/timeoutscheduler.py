import heapq
import logging
import sys
import threading
from collections.abc import MutableMapping
from typing import TypeVar
from weakref import WeakKeyDictionary

from reactivex import abc, typing
from reactivex.disposable import Disposable
from reactivex.internal.constants import DELTA_ZERO
from reactivex.internal.priorityqueue import PriorityQueue

from .periodicscheduler import PeriodicScheduler
from .scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

_TState = TypeVar("_TState")

# Cap on a single Condition.wait(). A far-future duetime would otherwise
# overflow the platform's time_t and kill the timer thread; we simply
# re-check the queue instead.
_MAX_WAIT = 3600.0

# Cancelled items are evicted lazily. Compact once they are both numerous
# enough to be worth a pass and a significant share of the queue, which keeps
# cancellation amortized O(1) while bounding the queue to ~2x the live items.
_PRUNE_THRESHOLD = 16


class TimeoutScheduler(PeriodicScheduler):
    """A scheduler that schedules work via timed callbacks.

    Uses a single dedicated timer thread to track due times, and runs each
    fired action on its own daemon thread. This avoids spawning one OS thread
    per *pending* timeout -- pending timeouts cost a queue entry -- while
    keeping user callbacks off the timer thread, so a blocking or nested
    handler cannot stall other timeouts. Cancellation removes the item from
    the timer queue.

    Prefer :meth:`singleton` (also used by ``TimeoutScheduler()``). Disposing
    the process-wide singleton is unsupported and will break subsequent
    timeout-based operators.
    """

    _lock = threading.Lock()
    _global: MutableMapping[type, "TimeoutScheduler"] = WeakKeyDictionary()

    _thread: typing.Startable | None
    _condition: threading.Condition
    _queue: PriorityQueue[ScheduledItem]
    _cancelled: int

    @classmethod
    def singleton(cls) -> "TimeoutScheduler":
        with TimeoutScheduler._lock:
            try:
                self = TimeoutScheduler._global[cls]
            except KeyError:
                self = super().__new__(cls)
                PeriodicScheduler.__init__(self)
                self._thread = None
                self._condition = threading.Condition(threading.Lock())
                self._queue = PriorityQueue()
                self._cancelled = 0
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
            if self._queue.peek() is si:
                self._condition.notify()
            self._ensure_thread()

        return Disposable(lambda: self._cancel(si))

    def _cancel(self, item: ScheduledItem) -> None:
        # Dispose before taking the gate: the disposable set by the action is
        # user code, and it may re-enter the scheduler -- cancelling a nested
        # timer, say -- while the condition's lock is not reentrant.
        item.cancel()

        with self._condition:
            if not self._queue:
                return

            if self._queue.peek() is item:
                # Drop the head eagerly, so the timer thread does not sleep
                # until a duetime nobody is waiting for any more.
                self._queue.dequeue()
                self._condition.notify()
                return

            # This count is deliberately approximate, and drifts both ways:
            # item.cancel() above runs outside the gate, so a concurrent
            # _prune may have evicted this item before we count it, and the
            # timer thread may dequeue a cancelled item this counter never
            # saw. It only steers the heuristic below -- hence the max(0, ...)
            # guards where it is decremented, and the recount in _prune.
            self._cancelled += 1
            if self._cancelled >= _PRUNE_THRESHOLD and self._cancelled * 2 >= len(
                self._queue
            ):
                self._prune()

    def _prune(self) -> None:
        """Drops cancelled items from the queue. Call under the gate."""

        items = [entry for entry in self._queue.items if not entry[0].is_cancelled()]
        self._cancelled = 0
        if len(items) == len(self._queue.items):
            return

        heapq.heapify(items)
        self._queue.items = items
        if not items:
            self._queue.count = PriorityQueue.MIN_COUNT

    def _ensure_thread(self) -> None:
        """Ensures there is a timer thread running. Call under the gate."""

        if not self._thread:
            thread = threading.Thread(
                target=self._run, daemon=True, name="RxTimeoutTimer"
            )
            self._thread = thread
            started = False
            try:
                thread.start()
                started = True
            finally:
                if not started:
                    self._thread = None

    @staticmethod
    def _dispatch(item: ScheduledItem) -> None:
        """Runs a due action on its own daemon thread.

        Threads are daemons, so a running action never delays interpreter
        shutdown -- as with the ``threading.Timer`` this replaced.
        """

        def invoke() -> None:
            if item.is_cancelled():
                return
            try:
                item.invoke()
            except Exception:  # pylint: disable=broad-except
                # A Timer thread used to report this through
                # threading.excepthook. Keep it visible.
                log.exception("Unhandled exception in scheduled action")

        try:
            threading.Thread(target=invoke, daemon=True, name="RxTimeout").start()
        except RuntimeError:
            if sys.is_finalizing():
                # Nothing left to run the action on, and nobody left to tell.
                log.debug("interpreter is shutting down; dropped an action")
            else:
                # Out of OS threads. The action is lost, and whoever was
                # waiting on it -- a timeout's on_error, say -- is never
                # notified, so this must not be a debug-level event.
                log.exception("could not dispatch a scheduled action; dropped it")

    def _run(self) -> None:
        """Timer loop: wait for due items and run them off this thread."""

        try:
            while True:
                ready = self._collect_ready()
                if ready is None:
                    return

                for item in ready:
                    # Re-check: the item may have been cancelled since
                    # _collect_ready released the gate.
                    if not item.is_cancelled():
                        self._dispatch(item)
        except Exception:  # pylint: disable=broad-except
            log.exception("TimeoutScheduler timer thread stopped unexpectedly")
        finally:
            with self._condition:
                if self._thread is threading.current_thread():
                    self._thread = None

    def _collect_ready(self) -> list[ScheduledItem] | None:
        """Waits until items are due and returns them.

        Returns None once the queue has drained, meaning the timer thread
        should stop. ``_thread`` is cleared under the same lock acquisition
        that observed the empty queue, so a concurrent ``schedule_*`` either
        sees a live thread or starts a new one. Exceptional exit is handled
        by ``_run``.
        """

        with self._condition:
            while True:
                while self._queue and self._queue.peek().is_cancelled():
                    self._queue.dequeue()
                    self._cancelled = max(0, self._cancelled - 1)

                if not self._queue:
                    if self._thread is threading.current_thread():
                        self._thread = None
                    return None

                seconds = (self._queue.peek().duetime - self.now).total_seconds()
                if seconds > 0:
                    log.debug("timeout: %s", seconds)
                    self._condition.wait(min(seconds, _MAX_WAIT))
                    continue

                now = self.now
                ready: list[ScheduledItem] = []
                while self._queue and self._queue.peek().duetime <= now:
                    item = self._queue.dequeue()
                    if item.is_cancelled():
                        self._cancelled = max(0, self._cancelled - 1)
                    else:
                        ready.append(item)
                return ready


__all__ = ["TimeoutScheduler"]
