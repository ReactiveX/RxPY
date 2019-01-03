from rx.core import Disposable, Observable, typing
from .subscription import Subscription


class HotObservable(Observable):
    def __init__(self, scheduler: typing.Scheduler, messages) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []
        self.observers = []

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

    def _subscribe_core(self, observer: typing.Observer, scheduler: typing.Scheduler = None) -> typing.Disposable:
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            self.subscriptions[index] = Subscription(start, end)

        return Disposable.create(dispose_action)
