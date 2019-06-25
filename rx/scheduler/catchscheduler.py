from datetime import datetime
from typing import cast, Callable, Optional

from rx.core import typing
from rx.disposable import Disposable, SingleAssignmentDisposable

from .periodicscheduler import PeriodicScheduler


class CatchScheduler(PeriodicScheduler):

    def __init__(self,
                 scheduler: typing.Scheduler,
                 handler: Callable[[Exception], bool]
                 ) -> None:
        """Wraps a scheduler, passed as constructor argument, adding exception
        handling for scheduled actions. The handler should return True to
        indicate it handled the exception successfully. Falsy return values will
        be taken to indicate that the exception should be escalated (raised by
        this scheduler).

        Args:
            scheduler: The scheduler to be wrapped.
            handler: Callable to handle exceptions raised by wrapped scheduler.
        """

        super().__init__()
        self._scheduler: typing.Scheduler = scheduler
        self._handler: Callable[[Exception], bool] = handler
        self._recursive_original: Optional[typing.Scheduler] = None
        self._recursive_wrapper: Optional['CatchScheduler'] = None

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self._scheduler.now

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

        action = self._wrap(action)
        return self._scheduler.schedule(action, state=state)

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

        action = self._wrap(action)
        return self._scheduler.schedule_relative(duetime, action, state=state)

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

        action = self._wrap(action)
        return self._scheduler.schedule_absolute(duetime, action, state=state)

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

        schedule_periodic = getattr(self._scheduler, 'schedule_periodic')
        if not callable(schedule_periodic):
            raise NotImplementedError

        disp: SingleAssignmentDisposable = SingleAssignmentDisposable()
        failed: bool = False

        def periodic(state: Optional[typing.TState] = None) -> Optional[typing.TState]:
            nonlocal failed
            if failed:
                return None
            try:
                return action(state)
            except Exception as ex:
                failed = True
                if not self._handler(ex):
                    raise
                disp.dispose()
                return None

        scheduler = cast(PeriodicScheduler, self._scheduler)
        disp.disposable = scheduler.schedule_periodic(period, periodic, state=state)
        return disp

    def _clone(self, scheduler: typing.Scheduler) -> 'CatchScheduler':
        return CatchScheduler(scheduler, self._handler)

    def _wrap(self, action: typing.ScheduledAction) -> typing.ScheduledAction:
        parent = self

        def wrapped_action(self,
                           state: Optional[typing.TState]
                           ) -> Optional[typing.Disposable]:
            try:
                return action(parent._get_recursive_wrapper(self), state)
            except Exception as ex:
                if not parent._handler(ex):
                    raise
                return Disposable()

        return wrapped_action

    def _get_recursive_wrapper(self, scheduler) -> 'CatchScheduler':
        if self._recursive_wrapper is None or self._recursive_original != scheduler:
            self._recursive_original = scheduler
            wrapper = self._clone(scheduler)
            wrapper._recursive_original = scheduler
            wrapper._recursive_wrapper = wrapper
            self._recursive_wrapper = wrapper

        return self._recursive_wrapper
