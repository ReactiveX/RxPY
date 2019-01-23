import time
import logging
import threading
from typing import List

from rx import disposable
from rx.core import typing
from .schedulerbase import SchedulerBase
from .eventloopscheduler import EventLoopScheduler

log = logging.getLogger('Rx')


class NewThreadScheduler(SchedulerBase):
    """Creates an object that schedules each unit of work on a separate thread.
    """

    def __init__(self, thread_factory=None) -> None:
        super(NewThreadScheduler, self).__init__()

        def default_factory(target, args=None) -> threading.Thread:
            t = threading.Thread(target=target, args=args or [])
            t.setDaemon(True)
            return t

        self.thread_factory = thread_factory or default_factory

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
        return self.schedule_relative(dt - self.now, action, state=None)

    def schedule_periodic(self, period: typing.RelativeTime, action: typing.ScheduledPeriodicAction,
                          state: typing.TState = None) -> typing.Disposable:
        """Schedule a periodic piece of work."""

        secs = self.to_seconds(period)
        disposed: List[bool] = []

        s = [state]

        def run() -> None:
            while True:
                time.sleep(secs)
                if disposed:
                    return

                new_state = action(s[0])
                if new_state is not None:
                    s[0] = new_state

        thread = self.thread_factory(run)
        thread.start()

        def dispose():
            disposed.append(True)

        return disposable.create(dispose)

