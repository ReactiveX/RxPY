from typing import List

from rx import disposable
from rx.core import Observable, typing

from .subscription import Subscription


class ColdObservable(Observable):
    def __init__(self, scheduler, messages) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []

    def _subscribe_core(self, observer=None, scheduler=None) -> typing.Disposable:
        clock = self.scheduler.to_seconds(self.scheduler.now)
        self.subscriptions.append(Subscription(clock))
        index = len(self.subscriptions) - 1
        disp = disposable.CompositeDisposable()

        def get_action(notification):
            def action(scheduler, state):
                notification.accept(observer)
                return disposable.empty()
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

        return disposable.create(dispose)
