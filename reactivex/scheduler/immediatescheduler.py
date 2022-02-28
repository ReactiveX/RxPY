from threading import Lock
from typing import MutableMapping, Optional, TypeVar
from weakref import WeakKeyDictionary

from reactivex import abc, typing
from reactivex.internal.constants import DELTA_ZERO
from reactivex.internal.exceptions import WouldBlockException

from .scheduler import Scheduler

_TState = TypeVar("_TState")


class ImmediateScheduler(Scheduler):
    """Represents an object that schedules units of work to run immediately,
    on the current thread. You're not allowed to schedule timeouts using the
    ImmediateScheduler since that will block the current thread while waiting.
    Attempts to do so will raise a :class:`WouldBlockException`.
    """

    _lock = Lock()
    _global: MutableMapping[type, "ImmediateScheduler"] = WeakKeyDictionary()

    @classmethod
    def singleton(cls) -> "ImmediateScheduler":
        with ImmediateScheduler._lock:
            try:
                self = ImmediateScheduler._global[cls]
            except KeyError:
                self = super().__new__(cls)
                ImmediateScheduler._global[cls] = self
        return self

    def __new__(cls) -> "ImmediateScheduler":
        return cls.singleton()

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

        return self.invoke_action(action, state)

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

        duetime = self.to_timedelta(duetime)
        if duetime > DELTA_ZERO:
            raise WouldBlockException()

        return self.invoke_action(action, state)

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
        return self.schedule_relative(duetime - self.now, action, state)
