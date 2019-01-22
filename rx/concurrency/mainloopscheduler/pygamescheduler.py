import logging
from typing import Any
from datetime import timedelta, datetime

from rx.internal import PriorityQueue
from rx.core import typing
from rx.concurrency import ScheduledItem
from rx.concurrency.schedulerbase import SchedulerBase

pygame = None
log = logging.getLogger("Rx")


class PyGameScheduler(SchedulerBase):
    """A scheduler that schedules works for PyGame.

    http://www.pygame.org/docs/ref/time.html
    http://www.pygame.org/docs/ref/event.html"""

    def __init__(self, event_id=None):
        global pygame
        import pygame

        self.timer = None
        self.event_id = event_id or pygame.USEREVENT

        self.queue = PriorityQueue()

    def schedule(self, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        log.debug("PyGameScheduler.schedule(state=%s)", state)
        return self.schedule_relative(0, action, state)

    def run(self) -> None:
        while self.queue:
            item = self.queue.peek()
            diff = item.duetime - self.now
            if diff > timedelta(0):
                break

            item = self.queue.dequeue()
            if not item.is_cancelled():
                item.invoke()

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        dt = self.now + self.to_timedelta(duetime)
        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, dt)

        self.queue.enqueue(si)

        return si.disposable

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort)."""

        return self.schedule_relative(duetime - self.now, action, state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by
        this property."""

        return self.to_datetime(pygame.time.get_ticks())
