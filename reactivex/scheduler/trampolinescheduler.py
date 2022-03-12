import logging
from typing import Optional, TypeVar

from reactivex import abc, typing
from reactivex.abc.disposable import DisposableBase
from reactivex.abc.scheduler import ScheduledAction
from reactivex.internal.constants import DELTA_ZERO

from .scheduleditem import ScheduledItem
from .scheduler import Scheduler
from .trampoline import Trampoline

_TState = TypeVar("_TState")
log = logging.getLogger("Rx")


class TrampolineScheduler(Scheduler):
    """Represents an object that schedules units of work on the trampoline.
    You should never schedule timeouts using the *TrampolineScheduler*, as
    it will block the thread while waiting.

    Each instance has its own trampoline (and queue), and you can schedule work
    on it from different threads. Beware though, that the first thread to call
    a *schedule* method while the trampoline is idle will then remain occupied
    until the queue is empty.
    """

    def __init__(self) -> None:

        self._tramp = Trampoline()

    def get_trampoline(self) -> Trampoline:
        return self._tramp

    def schedule(
        self, action: abc.ScheduledAction[_TState], state: Optional[_TState] = None
    ) -> abc.DisposableBase:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return self.schedule_absolute(self.now, action, state=state)

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

        duetime = max(DELTA_ZERO, self.to_timedelta(duetime))
        return self.schedule_absolute(self.now + duetime, action, state=state)

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
        if dt > self.now:
            log.warning("Do not schedule blocking work!")
        item: ScheduledItem = ScheduledItem(self, state, action, dt)

        self.get_trampoline().run(item)

        return item.disposable

    def schedule_required(self) -> bool:
        """Test if scheduling is required.

        Gets a value indicating whether the caller must call a
        schedule method. If the trampoline is active, then it returns
        False; otherwise, if the trampoline is not active, then it
        returns True.
        """
        return self.get_trampoline().idle()

    def ensure_trampoline(
        self, action: ScheduledAction[_TState]
    ) -> Optional[DisposableBase]:
        """Method for testing the TrampolineScheduler."""

        if self.schedule_required():
            return self.schedule(action)

        return action(self, None)
