import threading

from rx import Observable
from rx.core.notification import OnCompleted, OnError, OnNext
from rx.scheduler import VirtualTimeScheduler
from rx.testing import TestScheduler
from rx.testing.recorded import Recorded


class TestSubscriber(object):
    def __init__(self, observable: Observable, scheduler: VirtualTimeScheduler = TestScheduler()) -> None:
        super().__init__()
        self.completed = threading.Event()
        self.messages = []

        def on_next(value) -> None:
            self.messages.append(Recorded(scheduler.clock, OnNext(value)))

        def on_error(error) -> None:
            self.messages.append(Recorded(scheduler.clock, OnError(error)))
            self.completed.set()

        def on_completed() -> None:
            self.messages.append(Recorded(scheduler.clock, OnCompleted()))
            self.completed.set()

        observable.subscribe(
            on_next=on_next,
            on_error=on_error,
            on_completed=on_completed
        )

    def results(self):
        self.completed.wait(timeout=0.1)
        return self.messages
