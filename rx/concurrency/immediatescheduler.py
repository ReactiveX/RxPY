from datetime import timedelta

from rx.core import Scheduler
from .schedulerbase import SchedulerBase

# Immediate Scheduler
SCHEDULER_NO_BLOCK_ERROR = "Scheduler is not allowed to block the thread"


class ImmediateScheduler(SchedulerBase):
    def schedule(self, action, state=None):
        """Schedules an action to be executed."""

        return self.invoke_action(action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        duetime = self.to_timedelta(duetime)
        if duetime > timedelta(0):
            raise Exception(SCHEDULER_NO_BLOCK_ERROR)

        return self.invoke_action(action, state)

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime."""

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state)


Scheduler.immediate = immediate_scheduler = ImmediateScheduler()
