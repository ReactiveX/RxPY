from abc import abstractmethod
import logging
from datetime import datetime
import threading
from typing import Any

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
        self._clock = initial_clock
        self._is_enabled = False
        self._lock = threading.Lock()
        self._queue: PriorityQueue[ScheduledItem[typing.TState]] = PriorityQueue()

        super().__init__()

    @property
    def now(self) -> datetime:
        """Gets the schedulers absolute time clock value as datetime offset."""

        return self.to_datetime(self._clock)

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        return self.schedule_absolute(self._clock, action, state=state)

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

        duetime = self.add(self._clock, self.to_seconds(duetime))
        return self.schedule_absolute(duetime, action, state=state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None):
        """Schedules an action to be executed at duetime."""

        si: ScheduledItem[typing.TState] = ScheduledItem(self, state, action, duetime)
        with self._lock:
            self._queue.enqueue(si)
        return si.disposable

    def start(self) -> None:
        """Starts the virtual time scheduler."""

        with self._lock:
            if self._is_enabled:
                return
            self._is_enabled = True

        spinning = 0
        while True:
            with self._lock:
                if not self._is_enabled or not self._queue:
                    break

                item: ScheduledItem[typing.TState] = self._queue.dequeue()

                if item.duetime > self._clock:
                    self._clock = item.duetime
                    spinning = 0

                elif spinning > MAX_SPINNING:
                    self._clock += 1.0
                    spinning = 0

            if not item.is_cancelled():
                item.invoke()
            spinning += 1

        self.stop()

    def stop(self) -> None:
        """Stops the virtual time scheduler."""

        with self._lock:
            self._is_enabled = False

    def advance_to(self, time: float) -> None:
        """Advances the schedulers clock to the specified absolute time,
        running all work til that point.

        Args:
            time: Absolute time to advance the schedulers clock to.
        """

        with self._lock:
            if self._clock > time:
                raise ArgumentOutOfRangeException()

            if self._clock == time or self._is_enabled:
                return

            self._is_enabled = True

        while True:
            with self._lock:
                if not self._is_enabled or not self._queue:
                    break

                item: ScheduledItem[typing.TState] = self._queue.peek()

                if item.duetime > time:
                    break

                if item.duetime > self._clock:
                    self._clock = item.duetime

                self._queue.dequeue()

            if not item.is_cancelled():
                item.invoke()

        with self._lock:
            self._is_enabled = False
            self._clock = time

    def advance_by(self, time: float) -> None:
        """Advances the schedulers clock by the specified relative time,
        running all work scheduled for that timespan.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        log.debug("VirtualTimeScheduler.advance_by(time=%s)", time)

        self.advance_to(self.add(self._clock, time))

    def sleep(self, time: float) -> None:
        """Advances the schedulers clock by the specified relative time.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        dt = self.add(self._clock, time)

        if self._clock > dt:
            raise ArgumentOutOfRangeException()

        with self._lock:
            self._clock = dt

    @staticmethod
    @abstractmethod
    def add(absolute, relative):
        raise NotImplementedError
