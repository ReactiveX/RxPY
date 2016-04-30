import logging

from rx.core import Disposable
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

log = logging.getLogger("Rx")


class TkinterScheduler(SchedulerBase):
    """A scheduler that schedules work via the Tkinter main event loop.

    http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/universal.html
    http://effbot.org/tkinterbook/widget.htm"""

    def __init__(self, master):
        self.master = master

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        alarm = self.master.after_idle(interval)

        def dispose():
            # nonlocal alarm
            self.master.after_cancel(alarm)

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        msecs = self.to_relative(duetime)
        if msecs == 0:
            return scheduler.schedule(action, state)

        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = self.invoke_action(action, state)

        log.debug("timeout: %s", msecs)
        alarm = self.master.after(msecs, interval)

        def dispose():
            # nonlocal alarm
            self.master.after_cancel(alarm)

        return CompositeDisposable(disposable, Disposable.create(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)

    def schedule_periodic(self, period, action, state=None):
        """Schedules a periodic piece of work to be executed in the tkinter
        mainloop.

        Keyword arguments:
        period -- Period in milliseconds for running the work periodically.
        action -- Action to be executed.
        state -- [Optional] Initial state passed to the action upon the first
            iteration.

        Returns the disposable object used to cancel the scheduled recurring
        action (best effort)."""

        state = [state]

        def interval():
            state[0] = action(state[0])
            alarm[0] = self.master.after(period, interval)

        log.debug("timeout: %s", period)
        alarm = [self.master.after(period, interval)]

        def dispose():
            # nonlocal alarm
            self.master.after_cancel(alarm[0])

        return Disposable.create(dispose)
