from rx import Observable, Observer
from rx.disposables import Disposable, CompositeDisposable

from .subscription import Subscription
from .reactive_assert import AssertList

class ColdObservable(Observable):
    def __init__(self, scheduler, messages):
        super(ColdObservable, self).__init__(self.subscribe)
        
        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = AssertList()

    def subscribe(self, on_next, on_error=None, on_completed=None):
        print ("ColdObservable:subscribe()")

        if isinstance(on_next, Observer):
            observer = on_next
        else: 
            observer = Observer(on_next, on_error, on_completed)
            
        observable = self
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1
        disposable = CompositeDisposable()
        
        def get_action(notification):
            def action(scheduler, state):
                notification.accept(observer)
                return Disposable.empty()
            return action

        for message in self.messages:
            notification = message.value
            print ("Notification: ", notification)
            
            # Don't make closures within a loop
            action = get_action(notification)

            disposable.add(observable.scheduler.schedule_relative(message.time, action))

        def dispose():
            print ("ColdObservable:dispose()")
            start = observable.subscriptions[index].subscribe
            end = observable.scheduler.clock
            observable.subscriptions[index] = Subscription(start, end)
            disposable.dispose()

        return Disposable.create(dispose)

    