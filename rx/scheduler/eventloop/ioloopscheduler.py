import logging
from datetime import datetime
from typing import Any, Optional

from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable, SingleAssignmentDisposable

from ..periodicscheduler import PeriodicScheduler


log = logging.getLogger("Rx")


class IOLoopScheduler(PeriodicScheduler):
    """A scheduler that schedules work via the Tornado I/O main event loop.

    Note, as of Tornado 6, this is just a wrapper around the asyncio loop.

    http://tornado.readthedocs.org/en/latest/ioloop.html"""

    def __init__(self, loop: Any) -> None:
        """Create a new IOLoopScheduler.

        Args:
            loop: The ioloop to use; typically, you would get this by
                tornado import ioloop; ioloop.IOLoop.current()
        """

        super().__init__()
        self._loop = loop

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
        disposed = False

        def interval() -> None:
            if not disposed:
                sad.disposable = self.invoke_action(action, state=state)

        self._loop.add_callback(interval)

        def dispose() -> None:
            nonlocal disposed
            disposed = True

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
            return self.schedule(action, state=state)

        sad = SingleAssignmentDisposable()

        def interval() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        log.debug("timeout: %s", seconds)
        timer = self._loop.call_later(seconds, interval)

        def dispose() -> None:
            self._loop.remove_timeout(timer)
            self.\
                _loop.remove_timeout(timer)

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
        return self.schedule_relative(duetime - self.now, action, state=state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return self.to_datetime(self._loop.time())
