import logging
from typing import Any, Optional, Set, TypeVar, cast

from reactivex import abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)

from ..periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")

log = logging.getLogger("Rx")


class WxScheduler(PeriodicScheduler):
    """A scheduler for a wxPython event loop."""

    def __init__(self, wx: Any) -> None:
        """Create a new WxScheduler.

        Args:
            wx: The wx module to use; typically, you would get this by
                import wx
        """

        super().__init__()
        self._wx = wx
        timer_class: Any = self._wx.Timer

        class Timer(timer_class):
            def __init__(self, callback: typing.Action) -> None:
                super().__init__()  # type: ignore
                self.callback = callback

            def Notify(self) -> None:
                self.callback()

        self._timer_class = Timer
        self._timers: Set[Timer] = set()

    def cancel_all(self) -> None:
        """Cancel all scheduled actions.

        Should be called when destroying wx controls to prevent
        accessing dead wx objects in actions that might be pending.
        """
        for timer in self._timers:
            timer.Stop()  # type: ignore

    def _wxtimer_schedule(
        self,
        time: typing.AbsoluteOrRelativeTime,
        action: typing.ScheduledSingleOrPeriodicAction[_TState],
        state: Optional[_TState] = None,
        periodic: bool = False,
    ) -> abc.DisposableBase:
        scheduler = self

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            nonlocal state
            if periodic:
                state = cast(typing.ScheduledPeriodicAction[_TState], action)(state)
            else:
                sad.disposable = cast(typing.ScheduledAction[_TState], action)(
                    scheduler, state
                )

        msecs = max(1, int(self.to_seconds(time) * 1000.0))  # Must be non-zero

        log.debug("timeout wx: %s", msecs)

        timer = self._timer_class(interval)
        # A timer can only be used from the main thread
        if self._wx.IsMainThread():
            timer.Start(msecs, oneShot=not periodic)  # type: ignore
        else:
            self._wx.CallAfter(timer.Start, msecs, oneShot=not periodic)  # type: ignore
        self._timers.add(timer)

        def dispose() -> None:
            timer.Stop()  # type: ignore
            self._timers.remove(timer)

        return CompositeDisposable(sad, Disposable(dispose))

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
        is_disposed = False

        def invoke_action() -> None:
            if not is_disposed:
                sad.disposable = action(self, state)

        self._wx.CallAfter(invoke_action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

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
        return self._wxtimer_schedule(duetime, action, state=state)

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
        return self._wxtimer_schedule(duetime - self.now, action, state=state)

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

        return self._wxtimer_schedule(period, action, state=state, periodic=True)
