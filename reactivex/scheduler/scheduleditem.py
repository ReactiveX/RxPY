from datetime import datetime
from typing import Any, Optional

from reactivex import abc
from reactivex.disposable import SingleAssignmentDisposable

from .scheduler import Scheduler


class ScheduledItem(object):
    def __init__(
        self,
        scheduler: Scheduler,
        state: Optional[Any],
        action: abc.ScheduledAction[Any],
        duetime: datetime,
    ) -> None:
        self.scheduler: Scheduler = scheduler
        self.state: Optional[Any] = state
        self.action: abc.ScheduledAction[Any] = action
        self.duetime: datetime = duetime
        self.disposable: SingleAssignmentDisposable = SingleAssignmentDisposable()

    def invoke(self) -> None:
        ret = self.scheduler.invoke_action(self.action, state=self.state)
        self.disposable.disposable = ret

    def cancel(self) -> None:
        """Cancels the work item by disposing the resource returned by
        invoke_core as soon as possible."""

        self.disposable.dispose()

    def is_cancelled(self) -> bool:
        return self.disposable.is_disposed

    def __lt__(self, other: "ScheduledItem") -> bool:
        return self.duetime < other.duetime

    def __gt__(self, other: "ScheduledItem") -> bool:
        return self.duetime > other.duetime

    def __eq__(self, other: Any) -> bool:
        try:
            return self.duetime == other.duetime
        except AttributeError:
            return NotImplemented
