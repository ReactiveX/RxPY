import types
import sys

from .linq.observable_creation import ObservableCreation
from .linq.standardsequenceoperators import ObservableLinq

from .concurrency import ImmediateScheduler, CurrentThreadScheduler
from .observer import Observer

class Observable(ObservableCreation, ObservableLinq):
    def __init__(self, subscribe):
        self._subscribe = subscribe

    def subscribe(self, on_next=None, on_error=None, on_completed=None):
        if not on_next or isinstance(on_next, types.FunctionType):
            observer = Observer(on_next, on_completed, on_error)
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
        
        return cls(subscribe)

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
            
        return cls(subscribe)

def main():
    #a = Observable.returnvalue(42)
    a = Observable.range(0, 10)
    #a = Enumerable.repeat(10, sys.maxint)
    #a = (a
    #    .where(lambda x: x > 3)
    #    .select(lambda x: x * 10)
    #    )

    #a = a \
    #    .where(lambda x: x > 3) \
    #    .select(lambda x: x * 10)

    a = a.take(2)

    #a.where([x for x in xs ])
    
    def debug(x):
        print("value: ", x)

    disp = a.subscribe(debug)
    print(disp)
    disp.dispose()
    #print b.to_array()

if __name__ == '__main__':
    main()