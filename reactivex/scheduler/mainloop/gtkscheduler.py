from typing import Any, Optional, TypeVar, cast

from reactivex import abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)

from ..periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")


class GtkScheduler(PeriodicScheduler):
    """A scheduler that schedules work via the GLib main loop
    used in GTK+ applications.

    See https://wiki.gnome.org/Projects/PyGObject
    """

    def __init__(self, glib: Any) -> None:
        """Create a new GtkScheduler.

        Args:
            glib: The GLib module to use; typically, you would get this by
                >>> import gi
                >>> gi.require_version('Gtk', '3.0')
                >>> from gi.repository import GLib
        """

        super().__init__()
        self._glib = glib

    def _gtk_schedule(
        self,
        time: typing.AbsoluteOrRelativeTime,
        action: typing.ScheduledSingleOrPeriodicAction[_TState],
        state: Optional[_TState] = None,
        periodic: bool = False,
    ) -> abc.DisposableBase:

        msecs = max(0, int(self.to_seconds(time) * 1000.0))

        sad = SingleAssignmentDisposable()

        stopped = False

        def timer_handler(_: Any) -> bool:
            if stopped:
                return False

            nonlocal state
            if periodic:
                state = cast(typing.ScheduledPeriodicAction[_TState], action)(state)
            else:
                sad.disposable = self.invoke_action(
                    cast(typing.ScheduledAction[_TState], action), state=state
                )

            return periodic

        self._glib.timeout_add(msecs, timer_handler, None)

        def dispose() -> None:
            nonlocal stopped
            stopped = True

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
        return self._gtk_schedule(0.0, action, state)

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
        return self._gtk_schedule(duetime, action, state=state)

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
        return self._gtk_schedule(duetime - self.now, action, state=state)

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

        return self._gtk_schedule(period, action, state=state, periodic=True)
