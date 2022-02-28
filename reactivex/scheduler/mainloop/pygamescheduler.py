import logging
import threading
from typing import Any, Optional, TypeVar

from reactivex import abc, typing
from reactivex.internal import PriorityQueue
from reactivex.internal.constants import DELTA_ZERO

from ..periodicscheduler import PeriodicScheduler
from ..scheduleditem import ScheduledItem

_TState = TypeVar("_TState")

log = logging.getLogger("Rx")


class PyGameScheduler(PeriodicScheduler):
    """A scheduler that schedules works for PyGame.

    Note that this class expects the caller to invoke run() repeatedly.

    http://www.pygame.org/docs/ref/time.html
    http://www.pygame.org/docs/ref/event.html"""

    def __init__(self, pygame: Any):
        """Create a new PyGameScheduler.

        Args:
            pygame: The PyGame module to use; typically, you would get this by
                import pygame
        """

        super().__init__()
        self._pygame = pygame  # TODO not used, refactor to actually use pygame?
        self._lock = threading.Lock()
        self._queue: PriorityQueue[ScheduledItem] = PriorityQueue()

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

        log.debug("PyGameScheduler.schedule(state=%s)", state)
        return self.schedule_absolute(self.now, action, state=state)

    def schedule_relative(
        self,
        duetime: typing.RelativeTime,
        action: typing.ScheduledAction[_TState],
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

        duetime = max(DELTA_ZERO, self.to_timedelta(duetime))
        return self.schedule_absolute(self.now + duetime, action, state=state)

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: typing.ScheduledAction[_TState],
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

        duetime = self.to_datetime(duetime)
        si: ScheduledItem = ScheduledItem(self, state, action, duetime)

        with self._lock:
            self._queue.enqueue(si)

        return si.disposable

    def run(self) -> None:
        while self._queue:
            with self._lock:
                item: ScheduledItem = self._queue.peek()
                diff = item.duetime - self.now

                if diff > DELTA_ZERO:
                    break

                item = self._queue.dequeue()

            if not item.is_cancelled():
                item.invoke()
