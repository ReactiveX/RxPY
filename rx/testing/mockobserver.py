from typing import Any, List, TypeVar

from rx.core.abc import ObserverBase
from rx.core.notification import OnCompleted, OnError, OnNext
from rx.scheduler import VirtualTimeScheduler

from .recorded import Recorded

_T = TypeVar("_T")


class MockObserver(ObserverBase[_T]):
    def __init__(self, scheduler: VirtualTimeScheduler) -> None:
        self.scheduler: VirtualTimeScheduler = scheduler
        self.messages: List[Recorded] = []

    def on_next(self, value: Any) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnNext(value)))

    def on_error(self, error: Exception) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnError(error)))

    def on_completed(self) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnCompleted()))
