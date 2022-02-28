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


class TwistedScheduler(PeriodicScheduler):
    """A scheduler that schedules work via the Twisted reactor mainloop."""

    def __init__(self, reactor: Any) -> None:
        """Create a new TwistedScheduler.

        Args:
            reactor: The reactor to use; typically, you would get this
                by from twisted.internet import reactor
        """

        super().__init__()
        self._reactor = reactor

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

        return self.schedule_relative(0.0, action, state=state)

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

        seconds = max(0.0, self.to_seconds(duetime))

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = action(self, state)

        log.debug("timeout: %s", seconds)
        timer = self._reactor.callLater(seconds, interval)

        def dispose() -> None:
            if not timer.called:
                timer.cancel()

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

        return self.to_datetime(float(self._reactor.seconds()))
