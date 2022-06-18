import logging
from datetime import timedelta
from typing import Any, Optional, Set, TypeVar

from reactivex import abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)

from ..periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")

log = logging.getLogger(__name__)


class QtScheduler(PeriodicScheduler):
    """A scheduler for a PyQt5/PySide2 event loop."""

    def __init__(self, qtcore: Any):
        """Create a new QtScheduler.

        Args:
            qtcore: The QtCore instance to use; typically you would get this by
                either import PyQt5.QtCore or import PySide2.QtCore
        """
        super().__init__()
        self._qtcore = qtcore
        self._periodic_timers: Set[Any] = set()

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
        msecs = max(0, int(self.to_seconds(duetime) * 1000.0))
        sad = SingleAssignmentDisposable()
        is_disposed = False

        def invoke_action() -> None:
            if not is_disposed:
                sad.disposable = action(self, state)

        log.debug("relative timeout: %sms", msecs)

        # Use static method, let Qt C++ handle QTimer lifetime
        self._qtcore.QTimer.singleShot(msecs, invoke_action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

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

        delta: timedelta = self.to_datetime(duetime) - self.now
        return self.schedule_relative(delta, action, state=state)

    def schedule_periodic(
        self,
        period: typing.RelativeTime,
        action: typing.ScheduledPeriodicAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules a periodic piece of work to be executed in the loop.

        Args:
             period: Period in seconds for running the work repeatedly.
             action: Action to be executed.
             state: [Optional] state to be given to the action function.

         Returns:
             The disposable object used to cancel the scheduled action
             (best effort).
        """
        msecs = max(0, int(self.to_seconds(period) * 1000.0))
        sad = SingleAssignmentDisposable()

        def interval() -> None:
            nonlocal state
            state = action(state)

        log.debug("periodic timeout: %sms", msecs)

        timer = self._qtcore.QTimer()
        timer.setSingleShot(not period)
        timer.timeout.connect(interval)
        timer.setInterval(msecs)
        self._periodic_timers.add(timer)
        timer.start()

        def dispose() -> None:
            timer.stop()
            self._periodic_timers.remove(timer)
            timer.deleteLater()

        return CompositeDisposable(sad, Disposable(dispose))
