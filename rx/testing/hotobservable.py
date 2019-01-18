from typing import List

from rx.core import Disposable, Observable, typing, abc
from rx.concurrency import VirtualTimeScheduler
from .subscription import Subscription


class HotObservable(Observable):
    def __init__(self, scheduler: VirtualTimeScheduler, messages) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []
        self.observers: List[abc.Observer] = []

        observable = self

        def get_action(notification):
            def action(scheduler, state):
                for observer in observable.observers[:]:
                    notification.accept(observer)
                return Disposable.empty()
            return action

        for message in self.messages:
            notification = message.value

            # Warning: Don't make closures within a loop
            action = get_action(notification)
            scheduler.schedule_absolute(message.time, action)

    def subscribe(self, observer=None, scheduler=None) -> typing.Disposable:
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            print("Dispose hot at: %s" % self.scheduler.to_relative(self.scheduler.now))

            self.subscriptions[index] = Subscription(start, end)

        return Disposable.create(dispose_action)
