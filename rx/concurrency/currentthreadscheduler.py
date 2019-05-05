import logging
import threading
import time
from typing import MutableMapping, Optional
from weakref import WeakKeyDictionary

from rx.core import typing
from rx.internal import PriorityQueue
from rx.internal.constants import DELTA_ZERO

from .schedulerbase import SchedulerBase
from .scheduleditem import ScheduledItem


log = logging.getLogger('Rx')


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


class _Local(threading.local):
    __slots__ = 'idle', 'queue'

    def __init__(self) -> None:
        super().__init__()
        self.idle: bool = True
        self.queue: PriorityQueue[
            ScheduledItem[typing.TState]] = PriorityQueue()


class CurrentThreadScheduler(SchedulerBase):
    """Represents an object that schedules units of work on the current thread.
    You never want to schedule timeouts using the CurrentThreadScheduler since
    that will block the current thread while waiting.

    Please note, there will be at most a single instance per thread -- calls to
    the constructor will just return the same instance if one already exists.

    Conversely, if you pass an instance to another thread, it will effectively
    behave as a separate scheduler, with its own queue. In particular, this
    implies that you can't make assumptions about the execution order of items
    that were scheduled by different threads -- even if they were submitted to
    what superficially appears to be a single scheduler instance.
    """

    _local = _Local()
    _global: MutableMapping[threading.Thread, 'CurrentThreadScheduler'] = WeakKeyDictionary()

    def __new__(cls) -> 'CurrentThreadScheduler':
        """Ensure that each thread has at most a single instance."""

        thread = threading.current_thread()
        self: 'CurrentThreadScheduler' = CurrentThreadScheduler._global.get(thread)
        if not self:
            self = super().__new__(cls)
            CurrentThreadScheduler._global[thread] = self
        return self

    def __init__(self) -> None:
        """Creates a scheduler that schedules work as soon as possible
        on the current thread."""
        super().__init__()

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

        return self.schedule_absolute(self.now, action, state=state)

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

        duetime = SchedulerBase.normalize(self.to_timedelta(duetime))
        return self.schedule_absolute(self.now + duetime, action, state=state)

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

        if duetime > self.now:
            log.warning("Do not schedule blocking work!")

        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, duetime)

        local: _Local = CurrentThreadScheduler._local
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
        return CurrentThreadScheduler._local.idle

    def ensure_trampoline(self, action):
        """Method for testing the CurrentThreadScheduler."""

        if self.schedule_required():
            return self.schedule(action)

        return action(self, None)


current_thread_scheduler = CurrentThreadScheduler()
