import heapq
import logging
import threading
from collections import deque
from collections.abc import MutableMapping
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

# Cap on a single Condition.wait(). A far-future duetime would otherwise
# overflow the platform's time_t and kill the timer thread; we simply
# re-check the queue instead.
_MAX_WAIT = 3600.0

# Cancelled items are evicted lazily. Compact once they are both numerous
# enough to be worth a pass and a significant share of the queue, which keeps
# cancellation amortized O(1) while bounding the queue to ~2x the live items.
_PRUNE_THRESHOLD = 16


class _DispatchPool:
    """Runs scheduled actions on reusable daemon threads.

    The pool grows on demand rather than queueing behind busy workers: a
    scheduled action is user code that may block, or wait on another timeout
    scheduled on the same scheduler, so a bounded pool would starve or
    deadlock it. Idle workers are reused, and exit after ``IDLE_TIMEOUT``
    seconds without work.

    Workers are daemon threads and the pool registers no ``atexit`` hook, so
    a running action never delays interpreter shutdown. (``ThreadPoolExecutor``
    joins its workers on exit, and swallows action exceptions into futures
    nobody reads.)
    """

    IDLE_TIMEOUT = 60.0

    def __init__(self, name_prefix: str) -> None:
        self._name_prefix = name_prefix
        self._condition = threading.Condition(threading.Lock())
        self._work: deque[typing.Action] = deque()
        self._idle = 0
        self._spawned = 0

    def submit(self, work: typing.Action) -> None:
        """Runs *work* on a worker thread, starting one if all are busy."""

        with self._condition:
            self._work.append(work)
            self._condition.notify()
            if self._idle >= len(self._work):
                return

            self._spawned += 1
            name = f"{self._name_prefix}-{self._spawned}"

        thread = threading.Thread(target=self._run, name=name, daemon=True)
        try:
            thread.start()
        except RuntimeError:  # interpreter is shutting down
            log.debug("could not start %s", name)

    def _run(self) -> None:
        while True:
            with self._condition:
                while not self._work:
                    self._idle += 1
                    signalled = self._condition.wait(self.IDLE_TIMEOUT)
                    self._idle -= 1
                    if not signalled and not self._work:
                        return

                work = self._work.popleft()

            try:
                work()
            except Exception:  # pylint: disable=broad-except
                # A Timer thread used to report this through
                # threading.excepthook. Keep it visible, but keep the worker.
                log.exception("Unhandled exception in scheduled action")


class TimeoutScheduler(PeriodicScheduler):
    """A scheduler that schedules work via timed callbacks.

    Uses a single dedicated timer thread to track due times and dispatches
    each fired action onto a pool of daemon worker threads. This avoids
    spawning one OS thread per *pending* timeout -- pending timeouts cost a
    queue entry -- while keeping user callbacks off the timer thread, so a
    blocking or nested handler cannot stall other timeouts. The pool grows on
    demand for exactly that reason. Cancellation removes the item from the
    timer queue.

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
    _cancelled: int
    _pool: _DispatchPool

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
                self._cancelled = 0
                self._pool = _DispatchPool(f"{cls.__name__}-worker")
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
            thread = self._thread_factory(self._run)
            self._thread = thread
            thread.start()

    def _run(self) -> None:
        """Timer loop: wait for due items and dispatch them to the pool."""

        try:
            while True:
                ready = self._collect_ready()
                if ready is None:
                    return

                for item in ready:
                    if item.is_cancelled():
                        continue
                    try:
                        self._pool.submit(item.invoke)
                    except Exception:  # pylint: disable=broad-except
                        # Dispatching one action must not take down the loop.
                        log.exception("Could not dispatch a scheduled action")
        except Exception:  # pylint: disable=broad-except
            log.exception("TimeoutScheduler timer thread stopped unexpectedly")

    def _collect_ready(self) -> list[ScheduledItem] | None:
        """Waits until items are due and returns them.

        Returns None once the queue has drained, meaning the timer thread
        should stop. ``_thread`` is cleared under the same lock acquisition
        that observed the empty queue -- on the way out of a failure too, so
        that ``_ensure_thread`` never mistakes a dead thread for a live one
        and stops firing timeouts altogether. Either way a concurrent
        ``schedule_*`` sees a live thread or starts a new one.
        """

        with self._condition:
            try:
                return self._collect_ready_core()
            except BaseException:
                self._thread = None
                raise

    def _collect_ready_core(self) -> list[ScheduledItem] | None:
        """Body of :meth:`_collect_ready`. Call under the gate."""

        while True:
            while self._queue and self._queue.peek().is_cancelled():
                self._queue.dequeue()
                self._cancelled = max(0, self._cancelled - 1)

            if not self._queue:
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
