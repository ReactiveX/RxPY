import types

from rx import Observable, Observer
from rx.disposables import Disposable
from .subscription import Subscription

class HotObservable(Observable):
    def __init__(self, scheduler, messages):
        print ("HotObservable:__init__()")
        Observable.__init__(self, self.subscribe)

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []
        self.observers = []

        observable = self

        def wrapper(message, inner_notification):
            def action(scheduler, state):
                """HotObservable:wrapper:action"""

                for observer in observable.observers:
                    inner_notification.accept(observer)            
                return Disposable.empty()
            
            scheduler.schedule_absolute(message.time, action)
    
        for message in self.messages:
            notification = message.value

            wrapper(message, notification)
            
    def subscribe(self, on_next, on_error=None, on_completed=None):
        print ("HotObservable:subscribe()")

        if type(on_next) == types.FunctionType:
            observer = Observer(on_next, on_error, on_completed)
        else: 
            observer = on_next

        observable = self
        self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1 

        def dispose_action():
            print ("HotObservable:subscribe:dispose_action(%s)" % self.scheduler.clock)
            observable.observers.remove(observer)
            observable.subscriptions[index] = Subscription(observable.subscriptions[index].subscribe, observable.scheduler.clock)

        return Disposable.create(dispose_action)

    