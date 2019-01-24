import logging
import threading
from datetime import datetime
from typing import Any, List, Optional

from rx import disposable
from rx.core import typing
from rx.concurrency import ScheduledItem
from rx.internal.exceptions import DisposedException
from rx.internal.priorityqueue import PriorityQueue

from .schedulerbase import SchedulerBase

log = logging.getLogger('Rx')


class EventLoopScheduler(SchedulerBase, typing.Disposable):
    """Creates an object that schedules units of work on a designated
    thread."""

    def __init__(self, thread_factory=None, exit_if_empty=False) -> None:
        super(EventLoopScheduler, self).__init__()
        self.is_disposed = False

        def default_factory(target):
            t = threading.Thread(target=target)
            t.setDaemon(True)
            return t

        self.lock = threading.RLock()
        self.thread_factory = thread_factory or default_factory
        self.thread: Optional[threading.Thread] = None
        self.timer: Optional[threading.Timer] = None
        self.condition = threading.Condition(self.lock)
        self.queue = PriorityQueue()
        self.ready_list: List[ScheduledItem] = []
        self.next_item = None

        self.exit_if_empty = exit_if_empty

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        if self.is_disposed:
            raise DisposedException()

        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, self.now)

        with self.condition:
            self.ready_list.append(si)
            self.condition.notify()  # signal that a new item is available
            self.ensure_thread()

        return disposable.create(si.cancel)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime."""

        dt: datetime = self.now + self.to_timedelta(duetime)
        return self.schedule_absolute(dt, action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime."""

        if self.is_disposed:
            raise DisposedException()

        dt = self.to_datetime(duetime)
        si: ScheduledItem[typing.TState]= ScheduledItem(self, state, action, dt)

        with self.condition:
            if dt < self.now:
                self.ready_list.append(si)
            else:
                self.queue.enqueue(si)
            self.condition.notify()  # signal that a new item is available
            self.ensure_thread()

        return disposable.create(si.cancel)

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledPeriodicAction, state: Any = None
                         ) -> typing.Disposable:
        """Schedule a periodic piece of work."""

        disposed: List[bool] = []

        s = [state]

        def tick(scheduler, state):
            if disposed:
                return

            self.schedule_relative(period, tick)
            new_state = action(s[0])
            if new_state is not None:
                s[0] = new_state

        self.schedule_relative(period, tick)

        def dispose():
            disposed.append(True)

        return disposable.create(dispose)

    def ensure_thread(self) -> None:
        """Ensures there is an event loop thread running. Should be
        called under the gate."""

        if not self.thread:
            thread = self.thread_factory(self.run)
            self.thread = thread
            thread.start()

    def run(self) -> None:
        """Event loop scheduled on the designated event loop thread.
        The loop is suspended/resumed using the event which gets set by
        calls to Schedule, the next item timer, or calls to dispose."""

        while True:
            ready: List[ScheduledItem] = []

            with self.condition:

                # The event could have been set by a call to dispose. This
                # takes priority over anything else. We quit the loop
                # immediately. Subsequent calls to Schedule won't ever create a
                # new thread.
                if self.is_disposed:
                    return

                while self.queue and self.queue.peek().duetime <= self.now:
                    item = self.queue.dequeue()
                    self.ready_list.append(item)

                if self.queue:
                    _next = self.queue.peek()
                    if self.next_item is None or _next != self.next_item:
                        self.next_item = _next
                        due = _next.duetime - self.now
                        seconds = due.total_seconds()
                        log.debug("timeout: %s", seconds)

                        self.timer = threading.Timer(seconds, self.tick, args=[_next])
                        self.timer.setDaemon(True)
                        self.timer.start()

                if self.ready_list:
                    ready = self.ready_list[:]
                    self.ready_list = []
                else:
                    self.condition.wait()

            for item in ready:
                if not item.is_cancelled():
                    item.invoke()

            if self.exit_if_empty:
                with self.condition:
                    if not self.ready_list and not self.queue:
                        self.thread = None
                        return

    def dispose(self) -> None:
        """Ends the thread associated with this scheduler. All
        remaining work in the scheduler queue is abandoned.
        """

        with self.condition:
            if self.timer:
                self.timer.cancel()

            if not self.is_disposed:
                self.is_disposed = True

    def tick(self, item) -> None:
        with self.condition:

            if not self.is_disposed:
                if self.queue.remove(item):
                    self.ready_list.append(item)

            self.condition.notify()  # signal that a new item is available

event_loop_scheduler = EventLoopScheduler()
