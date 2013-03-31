from rx import Observable
from rx.disposables import Disposable, CompositeDisposable

from .subscription import Subscription

class ColdObservable(Observable):
    def __init__(self, scheduler, messages):
        super(ColdObservable, self).__init__(self.subscribe)
        
        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []

    def subscribe(self, observer):
        observable = self
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1
        d = CompositeDisposable()
        
        for message in self.messages:
            notification = message.value
            
            def action(scheduler, state):
                notification.accept(observer)
                return Disposable.empty()

            d.add(observable.scheduler.schedule_relative(message.time, action))

        def action():
            start = observable.subscriptions[index].subscribe
            end = observable.scheduler.clock
            observable.subscriptions[index] = Subscription(start, end)
            d.dispose()

        return Disposable.create(action)

    