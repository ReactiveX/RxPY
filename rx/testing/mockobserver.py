from typing import Any, List, Optional

from rx.core.typing import Disposable, Observer, Observable, Scheduler
from rx.core.notification import OnNext, OnError, OnCompleted
from rx.scheduler import VirtualTimeScheduler

from .recorded import Recorded


class MockObserver(Observer):

    def __init__(self, scheduler: VirtualTimeScheduler) -> None:
        self.scheduler: VirtualTimeScheduler = scheduler
        self.messages: List[Recorded] = []

    def subscribe_to(self,
                     observable: Observable,
                     *,
                     scheduler: Optional[Scheduler] = None
                     ) -> Disposable:
        return observable.subscribe(self.on_next,
                                    self.on_error,
                                    self.on_completed,
                                    scheduler=scheduler)

    def on_next(self, value: Any) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnNext(value)))

    def on_error(self, error: Exception) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnError(error)))

    def on_completed(self) -> None:
        self.messages.append(Recorded(self.scheduler.clock, OnCompleted()))
