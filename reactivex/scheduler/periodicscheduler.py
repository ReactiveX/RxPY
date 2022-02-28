from datetime import datetime
from typing import Optional, TypeVar

from reactivex import abc, typing
from reactivex.disposable import Disposable, MultipleAssignmentDisposable

from .scheduler import Scheduler

_TState = TypeVar("_TState")


class PeriodicScheduler(Scheduler, abc.PeriodicSchedulerBase):
    """Base class for the various periodic scheduler implementations in this
    package as well as the mainloop sub-package.
    """

    def schedule_periodic(
        self,
        period: typing.RelativeTime,
        action: typing.ScheduledPeriodicAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules a periodic piece of work.

        Args:
            period: Period in seconds or timedelta for running the
                work periodically.
            action: Action to be executed.
            state: [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort).
        """

        disp: MultipleAssignmentDisposable = MultipleAssignmentDisposable()
        seconds: float = self.to_seconds(period)

        def periodic(
            scheduler: abc.SchedulerBase, state: Optional[_TState] = None
        ) -> Optional[Disposable]:
            if disp.is_disposed:
                return None

            now: datetime = scheduler.now

            try:
                state = action(state)
            except Exception:
                disp.dispose()
                raise

            time = seconds - (scheduler.now - now).total_seconds()
            disp.disposable = scheduler.schedule_relative(time, periodic, state=state)

            return None

        disp.disposable = self.schedule_relative(period, periodic, state=state)
        return disp
