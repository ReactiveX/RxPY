from datetime import datetime
from typing import Generic, Optional

from rx.core import typing
from rx.disposable import SingleAssignmentDisposable

from .schedulerbase import SchedulerBase


class ScheduledItem(Generic[typing.TState]):  # pylint: disable=unsubscriptable-object

    def __init__(self,
                 scheduler: SchedulerBase,
                 state: Optional[typing.TState],
                 action: typing.ScheduledAction,
                 duetime: datetime
                 ) -> None:
        self.scheduler: SchedulerBase = scheduler
        self.state: Optional[typing.TState] = state
        self.action: typing.ScheduledAction = action
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

    def __lt__(self, other: 'ScheduledItem') -> bool:
        return self.duetime < other.duetime

    def __gt__(self, other: 'ScheduledItem') -> bool:
        return self.duetime > other.duetime

    def __eq__(self, other: 'ScheduledItem') -> bool:
        return self.duetime == other.duetime
