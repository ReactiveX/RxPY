import logging
from typing import Any

from rx import disposable
from rx.core import typing
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

log = logging.getLogger("Rx")


class WxScheduler(SchedulerBase):

    """A scheduler for a wxPython event loop."""

    def __init__(self, wx):
        self.wx = wx
        self._timers = set()

        class Timer(wx.Timer):

            def __init__(self, callback):
                super(Timer, self).__init__()
                self.callback = callback

            def Notify(self):
                self.callback()

        self._timer_class = Timer

    def cancel_all(self):
        """Cancel all scheduled actions.

        Should be called when destroying wx controls to prevent
        accessing dead wx objects in actions that might be pending.
        """
        for timer in self._timers:
            timer.Stop()

    def _wxtimer_schedule(self, time, action, state, periodic=False):
        scheduler = self

        sad = SingleAssignmentDisposable()

        periodic_state = [state]

        def interval():
            if periodic:
                periodic_state[0] = action(periodic_state[0])
            else:
                sad.disposable = action(scheduler, state)

        log.debug("timeout: %s", msecs)

        msecs = int(self.to_seconds(time)*1000.0)
        if msecs == 0:
            msecs = 1  # wx.Timer doesn't support zero.

        timer = self._timer_class(interval)
        timer.Start(
            msecs,
            self.wx.TIMER_CONTINUOUS if periodic else self.wx.TIMER_ONE_SHOT
        )
        self._timers.add(timer)

        def dispose():
            timer.Stop()
            self._timers.remove(timer)

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule(self, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        return self._wxtimer_schedule(0, action, state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        return self._wxtimer_schedule(duetime, action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled
        action (best effort).
        """

        duetime = self.to_datetime(duetime)
        return self._wxtimer_schedule(duetime, action, state)

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledPeriodicAction,
                          state: typing.TState = None):
        """Schedules a periodic piece of work to be executed in the Qt
        mainloop.

        Args:
            period: Period in milliseconds for running the work
                periodically.
            action: Action to be executed.
            state: [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort)."""

        return self._wxtimer_schedule(period, action, state, periodic=True)
