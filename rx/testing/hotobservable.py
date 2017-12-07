from rx.core import Observer, AnonymousObserver, Observable, Disposable
from .subscription import Subscription
from .reactive_assert import AssertList


class HotObservable(Observable):
    def __init__(self, scheduler, messages):
        super(HotObservable, self).__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = AssertList()
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

    def subscribe(self, send=None, throw=None, close=None, observer=None):
        # Be forgiving and accept an un-named observer as first parameter
        if isinstance(send, Observer):
            observer = send
        elif not observer:
            observer = AnonymousObserver(send, throw, close)

        return self._subscribe_core(observer)

    def _subscribe_core(self, observer):
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
