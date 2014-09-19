import logging

from rx import Observable, Observer
from rx.abstractobserver import AbstractObserver
from rx.disposables import Disposable

from .subscription import Subscription
from .reactive_assert import AssertList

log = logging.getLogger("Rx")

class HotObservable(Observable):
    def __init__(self, scheduler, messages):
        log.debug("HotObservable.__init__()")
        Observable.__init__(self, self._subscribe)

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

    def _subscribe(self, observer):
        log.debug("HotObservable:subscribe()")

        observable = self
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            log.debug("HotObservable:subscribe:dispose_action(%s)" % self.scheduler.clock)
            observable.observers.remove(observer)
            start = observable.subscriptions[index].subscribe
            end = observable.scheduler.clock
            observable.subscriptions[index] = Subscription(start, end)

        return Disposable(dispose_action)

