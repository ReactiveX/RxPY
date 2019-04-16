import logging
import threading
from typing import Optional

from rx.disposable import Disposable
from rx.core import typing
from rx.internal.concurrency import default_thread_factory

from .eventloopscheduler import EventLoopScheduler
from .schedulerbase import SchedulerBase

log = logging.getLogger('Rx')


class NewThreadScheduler(SchedulerBase):
    """Creates an object that schedules each unit of work on a separate thread.
    """

    def __init__(self, thread_factory: Optional[typing.StartableFactory] = None) -> None:
        super(NewThreadScheduler, self).__init__()
        self.thread_factory = thread_factory or default_thread_factory

    def schedule(self, action: typing.ScheduledAction, state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed."""

        scheduler = EventLoopScheduler(thread_factory=self.thread_factory, exit_if_empty=True)
        return scheduler.schedule(action, state)

    def schedule_relative(self, duetime: typing.RelativeTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed after duetime."""

        scheduler = EventLoopScheduler(thread_factory=self.thread_factory, exit_if_empty=True)
        return scheduler.schedule_relative(duetime, action, state)

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: typing.ScheduledAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedules an action to be executed at duetime."""

        dt = SchedulerBase.to_datetime(duetime)
        return self.schedule_relative(dt - self.now, action, state=state)

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledPeriodicAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedule a periodic piece of work."""

        secs: float = self.to_seconds(period)
        disposed: threading.Event = threading.Event()

        s = state

        def run() -> None:
            while True:
                disposed.wait(secs)
                if disposed.is_set():
                    return

                nonlocal s
                new_state = action(s)
                if new_state is not None:
                    s = new_state

        thread = self.thread_factory(run)
        thread.start()

        def dispose() -> None:
            disposed.set()

        return Disposable(dispose)

