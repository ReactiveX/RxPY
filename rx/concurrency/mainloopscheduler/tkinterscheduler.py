import logging
from datetime import datetime, timedelta

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.concurrency.scheduler import Scheduler

log = logging.getLogger("Rx")

class TkinterScheduler(Scheduler):
    """A scheduler that schedules work via the Tkinter main event loop.

    http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/universal.html
    http://effbot.org/tkinterbook/widget.htm"""

    def __init__(self, master):
        self.master = master

    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        scheduler = self
        disposable = SingleAssignmentDisposable()

        def interval():
            disposable.disposable = action(scheduler, state)

        alarm = self.master.after_idle(interval)

        def dispose():
            # nonlocal alarm
            self.master.after_cancel(alarm)

        return CompositeDisposable(disposable, Disposable(dispose))

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
            disposable.disposable = action(scheduler, state)

        log.debug("timeout: %s", msecs)
        alarm = self.master.after(msecs, interval)

        def dispose():
            # nonlocal alarm
            self.master.after_cancel(alarm)

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now(), action, state)
