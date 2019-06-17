import logging
from threading import current_thread, Lock, Thread
from typing import Optional
from weakref import WeakKeyDictionary

from rx.core import typing
from rx.internal import PriorityQueue

from .scheduler import Scheduler
from .scheduleditem import ScheduledItem
from .trampoline import Trampoline

log = logging.getLogger('Rx')


class TrampolineScheduler(Scheduler):
    """Represents an object that schedules units of work on the current
    thread. You never want to schedule timeouts using the TrampolineScheduler
    since it will block the current thread while waiting.

    This class is different from :class:`CurrentThreadScheduler` in that it
    does not enforce a singleton instance per thread, and in that each instance
    uses its own private queue.

    As a result, you can nest schedulers -- e.g., suppose a TrampolineScheduler
    has two actions scheduled, A and B, and in the course of executing A another
    instance of TrampolineScheduler is created and scheduled to run C.
    The final order of things happening on the current thread is A, C, B.

    If you try something similar with the `:class:CurrentThreadScheduler` then,
    due to the fact that it is a singleton per thread, with a common shared
    queue, the order will be A, B, C.
    """

    def __init__(self) -> None:
        """Creates a scheduler that schedules work as soon as possible
        on the current thread."""

        self.queues: WeakKeyDictionary[
            Thread,
            Optional[PriorityQueue]
        ] = WeakKeyDictionary()
        self.lock = Lock()

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

        duetime = self.to_timedelta(duetime)
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

        queue: Optional[PriorityQueue] = self._get_queue()
        if queue is None:
            queue = PriorityQueue()
            queue.enqueue(si)

            self._set_queue(queue)
            try:
                Trampoline.run(queue)
            finally:
                self._set_queue(None)
        else:
            queue.enqueue(si)

        return si.disposable

    def _get_queue(self) -> Optional[PriorityQueue]:
        with self.lock:
            return self.queues.get(current_thread())

    def _set_queue(self, queue: Optional[PriorityQueue] = None):
        with self.lock:
            self.queues[current_thread()] = queue

    def schedule_required(self) -> bool:
        """Test if scheduling is required.

        Gets a value indicating whether the caller must call a
        schedule method. If the trampoline is active, then it returns
        False; otherwise, if the trampoline is not active, then it
        returns True.
        """
        return self._get_queue() is None

    def ensure_trampoline(self, action):
        """Method for testing the TrampolineScheduler."""

        if self.schedule_required():
            return self.schedule(action)

        return action(self, None)
