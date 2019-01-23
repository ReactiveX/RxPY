from rx.core import typing
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase


class GtkScheduler(SchedulerBase):
    """ A scheduler that schedules work via the GLib main loop
    used in GTK+ applications.

    See https://wiki.gnome.org/Projects/PyGObject
    """

    def _gtk_schedule(self, time, action, state, periodic=False):
        # Do not import GLib into global scope because Qt and GLib
        # don't like each other there
        from gi.repository import GLib

        scheduler = self
        msecs = int(self.to_seconds(time)*1000)

        sad = SingleAssignmentDisposable()

        periodic_state = [state]
        stopped = [False]

        def timer_handler(_):
            if stopped[0]:
                return False

            if periodic:
                periodic_state[0] = action(periodic_state[0])
            else:
                sad.disposable = action(scheduler, state)

            return periodic

        GLib.timeout_add(msecs, timer_handler, None)

        def dispose():
            stopped[0] = True

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""
        return self._gtk_schedule(0, action, state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: {timedelta} Relative time after which to execute the action.
            action: {Function} Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        return self._gtk_schedule(duetime, action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: {datetime} Absolute time after which to execute the action.
            action: {Function} Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        duetime = self.to_datetime(duetime)
        return self._gtk_schedule(duetime, action, state)

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
            recurring action (best effort).
        """

        return self._gtk_schedule(period, action, state, periodic=True)
