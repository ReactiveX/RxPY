# Current Thread Scheduler
import time
import logging
import threading
from datetime import timedelta

from rx.core import typing
from rx.internal import PriorityQueue

from .schedulerbase import SchedulerBase
from .scheduleditem import ScheduledItem

log = logging.getLogger('Rx')

DELTA_ZERO = timedelta(0)


class Trampoline(object):
    @classmethod
    def run(cls, queue: PriorityQueue[ScheduledItem[typing.TState]]) -> None:
        while queue:
            item: ScheduledItem = queue.peek()
            if item.is_cancelled():
                queue.dequeue()
            else:
                diff = item.duetime - item.scheduler.now
                if diff <= DELTA_ZERO:
                    item.invoke()
                    queue.dequeue()
                else:
                    time.sleep(diff.total_seconds())


class CurrentThreadScheduler(SchedulerBase):
    """Represents an object that schedules units of work on the current
    thread. You never want to schedule timeouts using the
    CurrentThreadScheduler since it will block the current thread while
    waiting.
    """

    class _Local(threading.local):
        __slots__ = 'idle', 'queue'

        def __init__(self):
            self.idle: bool = True
            self.queue: PriorityQueue[ScheduledItem[typing.TState]] = PriorityQueue()

    def __init__(self) -> None:
        """Creates a scheduler that schedules work as soon as possible
        on the current thread."""

        self._local = CurrentThreadScheduler._Local()

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        #log.debug("CurrentThreadScheduler.schedule(state=%s)", state)
        return self.schedule_absolute(self.now, action, state=state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime."""

        duetime = SchedulerBase.normalize(self.to_timedelta(duetime))

        if duetime > DELTA_ZERO:
            log.warning("Do not schedule blocking work!")

        return self.schedule_absolute(self.now + duetime, action, state=state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime."""

        duetime = self.to_datetime(duetime)

        if duetime > self.now:
            log.warning("Do not schedule blocking work!")

        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, duetime)

        local: CurrentThreadScheduler._Local = self._local
        local.queue.enqueue(si)
        if local.idle:
            local.idle = False
            try:
                Trampoline.run(local.queue)
            finally:
                local.idle = True
                local.queue.clear()

        return si.disposable

    def schedule_required(self) -> bool:
        """Test if scheduling is required.

        Gets a value indicating whether the caller must call a
        schedule method. If the trampoline is active, then it returns
        False; otherwise, if the trampoline is not active, then it
        returns True.
        """
        return self._local.idle

    def ensure_trampoline(self, action):
        """Method for testing the CurrentThreadScheduler."""

        if self.schedule_required():
            return self.schedule(action)

        return action(self, None)


current_thread_scheduler = CurrentThreadScheduler()
