from typing import List

from rx.disposable import Disposable
from rx.core import Observable, typing
from rx.scheduler import VirtualTimeScheduler

from .recorded import Recorded
from .subscription import Subscription


class HotObservable(Observable):
    def __init__(self, scheduler: VirtualTimeScheduler, messages: List[Recorded]) -> None:
        super().__init__()

        self.scheduler: VirtualTimeScheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []
        self.observers: List[typing.Observer] = []

        observable = self

        def get_action(notification):
            def action(scheduler, state):
                for observer in observable.observers[:]:
                    notification.accept(observer)
                return Disposable()
            return action

        for message in self.messages:
            notification = message.value

            # Warning: Don't make closures within a loop
            action = get_action(notification)
            scheduler.schedule_absolute(message.time, action)

    def _subscribe_core(self, observer=None, scheduler=None) -> typing.Disposable:
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            self.subscriptions[index] = Subscription(start, end)

        return Disposable(dispose_action)
