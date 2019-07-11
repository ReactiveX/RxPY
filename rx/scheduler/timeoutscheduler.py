from threading import Lock, Timer
from typing import MutableMapping, Optional
from weakref import WeakKeyDictionary

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from .periodicscheduler import PeriodicScheduler


class TimeoutScheduler(PeriodicScheduler):
    """A scheduler that schedules work via a timed callback."""

    _lock = Lock()
    _global: MutableMapping[type, 'TimeoutScheduler'] = WeakKeyDictionary()

    @classmethod
    def singleton(cls) -> 'TimeoutScheduler':
        with TimeoutScheduler._lock:
            try:
                self = TimeoutScheduler._global[cls]
            except KeyError:
                self = super().__new__(cls)
                TimeoutScheduler._global[cls] = self
        return self

    def __new__(cls) -> 'TimeoutScheduler':
        return cls.singleton()

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

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state)

        timer = Timer(0, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose() -> None:
            timer.cancel()

        return CompositeDisposable(sad, Disposable(dispose))

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

        seconds = self.to_seconds(duetime)
        if seconds <= 0.0:
            return self.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state)

        timer = Timer(seconds, interval)
        timer.setDaemon(True)
        timer.start()

        def dispose() -> None:
            timer.cancel()

        return CompositeDisposable(sad, Disposable(dispose))

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
        return self.schedule_relative(duetime - self.now, action, state)
