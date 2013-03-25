import types

from rx import Observable, Observer
from rx.disposables import Disposable
from .subscription import Subscription

class HotObservable(Observable):
    def __init__(self, scheduler, messages):
        Observable.__init__(self, self.subscribe)

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []
        self.observers = []
        
        observable = self
        for message in self.messages:
            notification = message.value

            def action(scheduler, state):
                for observer in observable.observers:
                    notification.accept(observable)            
                return Disposable.empty()

            scheduler.schedule_absolute(message.time, action)
    
    def subscribe(self, on_next, on_error=None, on_completed=None):
        if type(on_next) == types.FunctionType:
            observer = Observer(on_next, on_error, on_completed)
        else: 
            observer = on_next

        observable = self
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def action():
            #idx = observable.observers.indexOf(observer)
            #observable.observers.splice(idx, 1)
            observable.observers.remove(observer)

            observable.subscriptions[index] = Subscription(observable.subscriptions[index].subscribe, observable.scheduler.clock)

        return Disposable.create(action)

    