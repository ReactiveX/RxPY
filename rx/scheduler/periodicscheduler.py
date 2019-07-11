from abc import abstractmethod
from datetime import datetime
from typing import Optional

from rx.core import typing
from rx.disposable import Disposable, MultipleAssignmentDisposable

from .scheduler import Scheduler


class PeriodicScheduler(Scheduler, typing.PeriodicScheduler):
    """Base class for the various periodic scheduler implementations in this
    package as well as the mainloop sub-package.
    """

    def schedule_periodic(self,
                          period: typing.RelativeTime,
                          action: typing.ScheduledPeriodicAction,
                          state: Optional[typing.TState] = None
                          ) -> typing.Disposable:
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

        def periodic(scheduler: typing.Scheduler,
                     state: Optional[typing.TState] = None
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

    @abstractmethod
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

        return NotImplemented

    @abstractmethod
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

        return NotImplemented

    @abstractmethod
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

        return NotImplemented
