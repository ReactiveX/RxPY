from rx.core import AnonymousObserver, Disposable, Observable
from .subscription import Subscription


class HotObservable(Observable):
    def __init__(self, scheduler, messages):
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

    def _subscribe_core(self, observer, scheduler=None):
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            print("DISPOSE!!!!!!!!!!!!!!!!!!")
            self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            print(end)
            self.subscriptions[index] = Subscription(start, end)

        return Disposable.create(dispose_action)
