from rx.core import AnonymousObserver, ObservableBase, Disposable
from .subscription import Subscription


class HotObservable(ObservableBase):
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

    def subscribe(self, observer=None, scheduler=None):
        return self._subscribe_core(observer, scheduler)

    def subscribe_callbacks(self, send=None, throw=None, close=None, scheduler=None):
        observer = AnonymousObserver(send, throw, close)
        return self.subscribe(observer, scheduler)

    def _subscribe_core(self, observer, scheduler=None):
        observable = self
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            observable.observers.remove(observer)
            start = observable.subscriptions[index].subscribe
            end = observable.scheduler.clock
            observable.subscriptions[index] = Subscription(start, end)

        return Disposable.create(dispose_action)
