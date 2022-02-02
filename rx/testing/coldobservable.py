from typing import List, Optional, TypeVar

from rx.core import Observable, abc
from rx.disposable import CompositeDisposable, Disposable
from rx.scheduler import VirtualTimeScheduler

from .subscription import Subscription

_T = TypeVar("_T")


class ColdObservable(Observable[_T]):
    def __init__(self, scheduler: VirtualTimeScheduler, messages) -> None:
        super().__init__()

        self.scheduler: VirtualTimeScheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []

    def _subscribe_core(self, observer=None, scheduler: Optional[abc.SubjectBase] = None) -> abc.DisposableBase:
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1
        disp = CompositeDisposable()

        def get_action(notification):
            def action(scheduler, state):
                notification.accept(observer)
                return Disposable()

            return action

        for message in self.messages:
            notification = message.value

            # Don't make closures within a loop
            action = get_action(notification)
            disp.add(self.scheduler.schedule_relative(message.time, action))

        def dispose() -> None:
            start = self.subscriptions[index].subscribe
            end = self.scheduler.to_seconds(self.scheduler.now)
            self.subscriptions[index] = Subscription(start, end)
            disp.dispose()

        return Disposable(dispose)
