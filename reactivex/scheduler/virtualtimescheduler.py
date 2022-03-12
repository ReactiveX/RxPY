import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Optional, TypeVar

from reactivex import abc, typing
from reactivex.abc.scheduler import AbsoluteTime
from reactivex.internal import ArgumentOutOfRangeException, PriorityQueue

from .periodicscheduler import PeriodicScheduler
from .scheduleditem import ScheduledItem

log = logging.getLogger("Rx")

MAX_SPINNING = 100

_TState = TypeVar("_TState")


class VirtualTimeScheduler(PeriodicScheduler):
    """Virtual Scheduler. This scheduler should work with either
    datetime/timespan or ticks as int/int"""

    def __init__(self, initial_clock: typing.AbsoluteTime = 0) -> None:
        """Creates a new virtual time scheduler with the specified
        initial clock value.

        Args:
            initial_clock: Initial value for the clock.
        """

        super().__init__()
        self._clock = initial_clock
        self._is_enabled = False
        self._lock: threading.Lock = threading.Lock()
        self._queue: PriorityQueue[ScheduledItem] = PriorityQueue()

    def _get_clock(self) -> AbsoluteTime:
        with self._lock:
            return self._clock

    clock = property(fget=_get_clock)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self.to_datetime(self._clock)

    def schedule(
        self, action: typing.ScheduledAction[_TState], state: Optional[_TState] = None
    ) -> abc.DisposableBase:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return self.schedule_absolute(self._clock, action, state=state)

    def schedule_relative(
        self,
        duetime: typing.RelativeTime,
        action: abc.ScheduledAction[_TState],
        state: Optional[_TState] = None,
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

        time: typing.AbsoluteTime = self.add(self._clock, duetime)
        return self.schedule_absolute(time, action, state=state)

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: abc.ScheduledAction[_TState],
        state: Optional[_TState] = None,
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
        with self._lock:
            self._queue.enqueue(si)
        return si.disposable

    def start(self) -> Any:
        """Starts the virtual time scheduler."""

        with self._lock:
            if self._is_enabled:
                return
            self._is_enabled = True

        spinning: int = 0

        while True:
            with self._lock:
                if not self._is_enabled or not self._queue:
                    break

                item: ScheduledItem = self._queue.dequeue()

                if item.duetime > self.now:
                    if isinstance(self._clock, datetime):
                        self._clock = item.duetime
                    else:
                        self._clock = self.to_seconds(item.duetime)
                    spinning = 0

                elif spinning > MAX_SPINNING:
                    if isinstance(self._clock, datetime):
                        self.clock += timedelta(microseconds=1000)
                    else:
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

    def advance_to(self, time: typing.AbsoluteTime) -> None:
        """Advances the schedulers clock to the specified absolute time,
        running all work til that point.

        Args:
            time: Absolute time to advance the schedulers clock to.
        """

        dt: datetime = self.to_datetime(time)
        with self._lock:
            if self.now > dt:
                raise ArgumentOutOfRangeException()

            if self.now == dt or self._is_enabled:
                return

            self._is_enabled = True

        while True:
            with self._lock:
                if not self._is_enabled or not self._queue:
                    break

                item: ScheduledItem = self._queue.peek()

                if item.duetime > dt:
                    break

                if item.duetime > self.now:
                    if isinstance(self._clock, datetime):
                        self._clock = item.duetime
                    else:
                        self._clock = self.to_seconds(item.duetime)

                self._queue.dequeue()

            if not item.is_cancelled():
                item.invoke()

        with self._lock:
            self._is_enabled = False
            if isinstance(self._clock, datetime):
                self._clock = dt
            else:
                self._clock = self.to_seconds(dt)

    def advance_by(self, time: typing.RelativeTime) -> None:
        """Advances the schedulers clock by the specified relative time,
        running all work scheduled for that timespan.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        log.debug("VirtualTimeScheduler.advance_by(time=%s)", time)

        self.advance_to(self.add(self.now, self.to_timedelta(time)))

    def sleep(self, time: typing.RelativeTime) -> None:
        """Advances the schedulers clock by the specified relative time.

        Args:
            time: Relative time to advance the schedulers clock by.
        """

        absolute = self.add(self.now, self.to_timedelta(time))
        dt: datetime = self.to_datetime(absolute)

        if self.now > dt:
            raise ArgumentOutOfRangeException()

        with self._lock:
            if isinstance(self._clock, datetime):
                self._clock = dt
            else:
                self._clock = self.to_seconds(dt)

    @classmethod
    def add(
        cls, absolute: typing.AbsoluteTime, relative: typing.RelativeTime
    ) -> typing.AbsoluteTime:
        """Adds a relative time value to an absolute time value.

        Args:
            absolute: Absolute virtual time value.
            relative: Relative virtual time value to add.

        Returns:
            The resulting absolute virtual time sum value.
        """

        return cls.to_datetime(absolute) + cls.to_timedelta(relative)
