import logging

from typing import cast, Any, Optional, Set

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from ..periodicscheduler import PeriodicScheduler


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

            def __init__(self, callback) -> None:
                super().__init__()
                self.callback = callback

            def Notify(self):
                self.callback()

        self._timer_class = Timer
        self._timers: Set[Timer] = set()

    def cancel_all(self) -> None:
        """Cancel all scheduled actions.

        Should be called when destroying wx controls to prevent
        accessing dead wx objects in actions that might be pending.
        """
        for timer in self._timers:
            timer.Stop()

    def _wxtimer_schedule(self,
                          time: typing.AbsoluteOrRelativeTime,
                          action: typing.ScheduledSingleOrPeriodicAction,
                          state: Optional[typing.TState] = None,
                          periodic: bool = False
                          ) -> typing.Disposable:
        scheduler = self

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            nonlocal state
            if periodic:
                state = cast(typing.ScheduledPeriodicAction, action)(state)
            else:
                sad.disposable = cast(typing.ScheduledAction, action)(scheduler, state)

        msecs = max(1, int(self.to_seconds(time) * 1000.0))  # Must be non-zero

        log.debug("timeout wx: %s", msecs)

        timer = self._timer_class(interval)
        timer.Start(
            msecs,
            self._wx.TIMER_CONTINUOUS if periodic else self._wx.TIMER_ONE_SHOT
        )
        self._timers.add(timer)

        def dispose() -> None:
            timer.Stop()
            self._timers.remove(timer)

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule(self,
                 action: typing.ScheduledAction,
                 state: Optional[typing.TState] = None
                 ) -> typing.Disposable:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return self._wxtimer_schedule(0.0, action, state=state)

    def schedule_relative(self,
                          duetime: typing.RelativeTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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

    def schedule_absolute(self,
                          duetime: typing.AbsoluteTime,
                          action: typing.ScheduledAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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

    def schedule_periodic(self,
                          period: typing.RelativeTime,
                          action: typing.ScheduledPeriodicAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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
