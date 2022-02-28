import logging
from datetime import datetime
from typing import Any, Optional, TypeVar

from reactivex import abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)

from ..periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")
log = logging.getLogger("Rx")


class EventletScheduler(PeriodicScheduler):
    """A scheduler that schedules work via the eventlet event loop.

    http://eventlet.net/
    """

    def __init__(self, eventlet: Any) -> None:
        """Create a new EventletScheduler.

        Args:
            eventlet: The eventlet module to use; typically, you would get this
                by import eventlet
        """

        super().__init__()
        self._eventlet = eventlet

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

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        timer = self._eventlet.spawn(interval)

        def dispose() -> None:
            timer.kill()

        return CompositeDisposable(sad, Disposable(dispose))

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

        seconds = self.to_seconds(duetime)
        if seconds <= 0.0:
            return self.schedule(action, state=state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        timer = self._eventlet.spawn_after(seconds, interval)

        def dispose() -> None:
            timer.kill()

        return CompositeDisposable(sad, Disposable(dispose))

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
        return self.schedule_relative(duetime - self.now, action, state=state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self.to_datetime(self._eventlet.hubs.get_hub().clock())
