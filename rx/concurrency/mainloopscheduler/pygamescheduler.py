import logging
import threading

from datetime import datetime
from typing import Optional

from rx.internal import PriorityQueue
from rx.core import typing

from ..scheduleditem import ScheduledItem
from ..schedulerbase import SchedulerBase, DELTA_ZERO


pygame = None
log = logging.getLogger("Rx")


class PyGameScheduler(SchedulerBase):
    """A scheduler that schedules works for PyGame.

    Note that this class expects the caller to invoke run() repeatedly.

    http://www.pygame.org/docs/ref/time.html
    http://www.pygame.org/docs/ref/event.html"""

    def __init__(self) -> None:
        global pygame
        import pygame

        self.timer = None
        self.lock = threading.RLock()
        self.queue: PriorityQueue[ScheduledItem[typing.TState]] = PriorityQueue()

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

        log.debug("PyGameScheduler.schedule(state=%s)", state)
        return self.schedule_relative(0.0, action, state=state)

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

        dt = self.now + self.to_timedelta(duetime)
        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, dt)

        with self.lock:
            self.queue.enqueue(si)

        return si.disposable

    def schedule_absolute(self,
                          duetime: typing.AbsoluteTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return self.schedule_relative(duetime - self.now, action, state=state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.
        """

        return datetime.utcnow()

    def run(self) -> None:
        with self.lock:
            while self.queue:
                item: ScheduledItem[typing.TState] = self.queue.peek()
                diff = item.duetime - self.now

                if diff > DELTA_ZERO:
                    break

                item = self.queue.dequeue()
                if not item.is_cancelled():
                    item.invoke()
