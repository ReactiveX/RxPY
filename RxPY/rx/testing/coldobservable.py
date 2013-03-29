from rx import Observable

from .subscription import Subscription

class ColdObservable(Observable):
    def __init__(self, scheduler, messages):
        Observable.__init__(this, subscribe)
        
        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []

    def subscribe(self, observer):
        observable = self
        self.subscriptions.push(Subscription(self.scheduler.clock))
        index = self.subscriptions.length - 1
        d = CompositeDisposable()
        
        for message in self.messages:
            notification = message.value
            
            def action(scheduler, state):
                notification.accept(observer)
                return Disposable.empty()

            d.add(observable.scheduler.schedule_relative(message.time, action))

        def action():
            observable.subscriptions[index] = Subscription(observable.subscriptions[index].subscribe, observable.scheduler.clock)
            d.dispose()

        return Disposable.create(action)

    