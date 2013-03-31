import types

from .linq.observable_creation import ObservableCreation

from .concurrency import ImmediateScheduler, CurrentThreadScheduler
from .observer import Observer

class Observable(ObservableCreation):
    """Represents a push-style collection."""

    def __init__(self, subscribe):
        self._subscribe = subscribe

    def subscribe(self, on_next=None, on_error=None, on_completed=None):
        """Subscribes an observer to the observable sequence. Returns he source
        sequence whose subscriptions and unsubscriptions happen on the specified scheduler.
        
        1 - source.subscribe()
        2 - source.subscribe(observer)
        3 - source.subscribe(on_next)
        4 - source.subscribe(on_next, on_error)
        5 - source.subscribe(on_next, on_error, on_completed)
        
        Keyword arguments:
        observer_or_on_next -- [Optional] The object that is to receive notifications or an action to invoke for each element in the observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination of the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination of the observable sequence.
        """
        if not on_next or isinstance(on_next, types.FunctionType):
            observer = Observer(on_next, on_error, on_completed)
        else:
            observer = on_next

        return self._subscribe(observer)

    @classmethod
    def returnvalue(cls, value, scheduler=None):
        scheduler = scheduler or ImmediateScheduler()

        def subscribe(observer):
            def action(scheduler, state=None):
                observer.on_next(value)
                observer.on_completed()

            return scheduler.schedule(action)
        
        #return cls(subscribe)
        return Observable(subscribe)

    @classmethod
    def range(cls, start, count, scheduler=None):
        scheduler = scheduler or CurrentThreadScheduler()
        
        def subscribe(observer):
            def action(scheduler, i):
                print("Observable:range:subscribe:action", scheduler, i)
                if i < count:
                    observer.on_next(start + i)
                    scheduler(i + 1)
                else:
                    #print "completed"
                    observer.on_completed()
                
            return scheduler.schedule_recursive(action, 0)
            
        return Observable(subscribe)
