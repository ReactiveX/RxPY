from typing import Optional

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from ..schedulerbase import SchedulerBase


class GtkScheduler(SchedulerBase):
    """ A scheduler that schedules work via the GLib main loop
    used in GTK+ applications.

    See https://wiki.gnome.org/Projects/PyGObject
    """

    def _gtk_schedule(self,
                      time: typing.AbsoluteOrRelativeTime,
                      action: typing.ScheduledSingleOrPeriodicAction,
                      state: Optional[typing.TState] = None,
                      periodic: bool = False
                      ) -> typing.Disposable:
        # Do not import GLib into global scope because Qt and GLib
        # don't like each other there
        from gi.repository import GLib

        msecs = int(self.to_seconds(time) * 1000.0)

        sad = SingleAssignmentDisposable()

        periodic_state = state
        stopped = False

        def timer_handler(_) -> bool:
            if stopped:
                return False

            if periodic:
                nonlocal periodic_state
                periodic_state = action(periodic_state)
            else:
                sad.disposable = self.invoke_action(action, state=state)

            return periodic

        GLib.timeout_add(msecs, timer_handler, None)

        def dispose() -> None:
            nonlocal stopped
            stopped = True

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
        return self._gtk_schedule(0.0, action, state)

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
        return self._gtk_schedule(duetime, action, state=state)

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
        return self._gtk_schedule(duetime - self.now, action, state=state)

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

        return self._gtk_schedule(period, action, state=state, periodic=True)
