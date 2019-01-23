import logging
from typing import Any
from datetime import datetime

from rx import disposable
from rx.core import typing
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable
from rx.concurrency.schedulerbase import SchedulerBase

log = logging.getLogger("Rx")

eventlet = None


class EventLetEventScheduler(SchedulerBase):
    """A scheduler that schedules work via the eventlet event loop.

    http://eventlet.net/
    """

    def __init__(self) -> None:
        # Lazy import
        global eventlet
        import eventlet
        import eventlet.hubs

    def schedule(self, action: typing.ScheduledAction, state: Any = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        timer = [eventlet.spawn(interval)]

        def dispose():
            timer[0].kill()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        scheduler = self
        seconds = self.to_seconds(duetime)
        if not seconds:
            return scheduler.schedule(action, state)

        sad = SingleAssignmentDisposable()

        def interval():
            sad.disposable = self.invoke_action(action, state)

        log.debug("timeout: %s", seconds)
        timer = [eventlet.spawn_after(seconds, interval)]

        def dispose():
            # nonlocal timer
            timer[0].kill()

        return CompositeDisposable(sad, disposable.create(dispose))

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time after which to execute the action.
            action: Action to be executed.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort)."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)

    @property
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by
        this property."""

        return self.to_datetime(eventlet.hubs.hub.time.time())
