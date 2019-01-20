from typing import Any
from datetime import datetime

from rx.core import Scheduler, typing
from rx.disposables import SingleAssignmentDisposable


def default_sub_comparer(x, y):
    return 0 if x == y else 1 if x > y else -1


class ScheduledItem:
    def __init__(self, scheduler: Scheduler, state: Any, action: typing.ScheduledAction, duetime: typing.AbsoluteTime):
        self.scheduler = scheduler
        self.state = state
        self.action = action
        self.duetime = duetime
        self.disposable: typing.Disposable = SingleAssignmentDisposable()

    def invoke(self):
        ret = self.scheduler.invoke_action(self.action, self.state)
        self.disposable.disposable = ret

    def cancel(self):
        """Cancels the work item by disposing the resource returned by
        invoke_core as soon as possible."""

        self.disposable.dispose()

    def is_cancelled(self):
        return self.disposable.is_disposed

    def __lt__(self, other):
        return self.duetime < other.duetime

    def __gt__(self, other):
        return self.duetime > other.duetime

    def __eq__(self, other):
        return self.duetime == other.duetime
