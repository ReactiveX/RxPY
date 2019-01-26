import logging
from datetime import datetime
from typing import Optional, Any

from rx.internal import PriorityQueue, ArgumentOutOfRangeException
from rx.core import typing

from .schedulerbase import SchedulerBase
from .scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

MAX_SPINNING = 100

class VirtualTimeScheduler(SchedulerBase):
    """Virtual Scheduler. This scheduler should work with either
    datetime/timespan or ticks as int/int"""

    def __init__(self, initial_clock=0.0) -> None:
        """Creates a new virtual time scheduler with the specified
        initial clock value and absolute time comparer.

        Args:
            initial_clock: Initial value for the clock.
            comparer: Comparer to determine causality of events based
                on absolute time.
        """
        self.clock = initial_clock

        self.is_enabled = False
        self.queue = PriorityQueue(1024)

        super().__init__()

    @property
    def now(self) -> datetime:
        """Gets the schedulers absolute time clock value as datetime offset."""

        return self.to_datetime(self.clock)

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        return self.schedule_absolute(self.clock, action, state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction, state: Any = None):
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] State passed to the action to be
                executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort)
        """

        runat = self.add(self.clock, self.to_seconds(duetime))
        return self.schedule_absolute(duetime=runat, action=action, state=state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None):
        """Schedules an action to be executed at duetime."""

        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, duetime)
        self.queue.enqueue(si)
        return si.disposable

    def start(self) -> None:
        """Starts the virtual time scheduler."""

        if self.is_enabled:
            return

        self.is_enabled = True

        spinning = 0
        while self.is_enabled:
            item = self.get_next()
            if not item:
                break

            if item.duetime > self.clock:
                self.clock = item.duetime
                spinning = 0

            if spinning > MAX_SPINNING:
                self.clock += 1.0
                spinning = 0

            item.invoke()
            spinning += 1

        self.is_enabled = False

    def stop(self) -> None:
        """Stops the virtual time scheduler."""

        self.is_enabled = False

    def advance_to(self, time: float) -> None:
        """Advances the schedulers clock to the specified time,
        running all work til that point.

        Args:
            time: Absolute time to advance the schedulers clock to.
        """

        if self.clock > time:
            raise ArgumentOutOfRangeException()

        if self.clock == time:
            return

        if self.is_enabled:
            return

        self.is_enabled = True

        while self.is_enabled:
            item = self.get_next()
            if not item:
                break

            if item.duetime > time:
                self.queue.enqueue(item)
                break

            if item.duetime > self.clock:
                self.clock = item.duetime

            item.invoke()

        self.is_enabled = False
        self.clock = time

    def advance_by(self, time: float) -> None:
        """Advances the schedulers clock by the specified relative time,
        running all work scheduled for that timespan.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        log.debug("VirtualTimeScheduler.advance_by(time=%s)", time)

        dt = self.add(self.clock, time)
        if self.clock > dt:
            raise ArgumentOutOfRangeException()
        self.advance_to(dt)

    def sleep(self, time: float) -> None:
        """Advances the schedulers clock by the specified relative time.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        dt = self.add(self.clock, time)

        if self.clock > dt:
            raise ArgumentOutOfRangeException()

        self.clock = dt

    def get_next(self) -> Optional[ScheduledItem]:
        """Returns the next scheduled item to be executed."""

        while self.queue:
            item = self.queue.dequeue()
            if not item.is_cancelled():
                return item

        return None

    @staticmethod
    def add(absolute, relative):
        raise NotImplementedError
