import types
from inspect import getargspec, getargvalues 

from rx import Observable, AnonymousObservable
from rx.subjects import Subject
from rx.observable import ObservableMeta
from rx.disposables import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.internal.basic import default_key_serializer, identity
from rx.internal import ArgumentOutOfRangeException
from rx.internal.utils import adapt_call
from .groupedobservable import GroupedObservable

class ObservableSkip(Observable, metaclass=ObservableMeta):
    """Note that we do some magic here by using a meta class to extend 
    Observable with the methods in this class"""
    
    def skip_while(self, predicate):
        """Bypasses elements in an observable sequence as long as a specified 
        condition is true and then returns the remaining elements. The 
        element's index is used in the logic of the predicate function.
        
        1 - source.skip_while(lambda value: value < 10)
        2 - source.skip_while(lambda value, index: value < 10 or index < 10)
        
        predicate -- A function to test each element for a condition; the 
            second parameter of the function represents the index of the 
            source element.
        
        Returns an observable sequence that contains the elements from the 
        input sequence starting at the first element in the linear series that
        does not pass the test specified by predicate.        
        """
        predicate = adapt_call(predicate)
        source = self

        def subscribe(observer):
            i, running = 0, False

            def on_next(value):
                nonlocal running, i
                if not running:
                    try:
                        running = not predicate(value, i)
                    except Exception as exn:
                        observer.on_error(exn)
                        return
                    else:
                        i += 1
        
                if running:
                    observer.on_next(value)
                
            return source.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    def take(self, count, scheduler=None):
        """Returns a specified number of contiguous elements from the start of
        an observable sequence, using the specified scheduler for the edge case
        of take(0).
        
        1 - source.take(5)
        2 - source.take(0, rx.Scheduler.timeout)
        
        Keyword arguments:
        count -- The number of elements to return.
        scheduler -- [Optional] Scheduler used to produce an OnCompleted 
            message in case count is set to 0.

        Returns an observable sequence that contains the specified number of 
        elements from the start of the input sequence.
        """

        if count < 0:
            raise ArgumentOutOfRangeException()
        
        if not count:
            return Observable.Empty(scheduler)
        
        observable = self
        def subscribe(observer):
            remaining = count

            def on_next(value):
                nonlocal remaining

                if remaining > 0:
                    remaining -= 1
                    observer.on_next(value)
                    if not remaining:
                        observer.on_completed()
                    
            return observable.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
    
    def take_while(self, predicate):
        """Returns elements from an observable sequence as long as a specified
        condition is true. The element's index is used in the logic of the 
        predicate function.
        
        1 - source.take_while(lambda value: value < 10)
        2 - source.take_while(lambda value, index: value < 10 or index < 10)
        
        Keyword arguments:
        predicate -- A function to test each element for a condition; the 
            second parameter of the function represents the index of the source
            element.

        Returns an observable sequence that contains the elements from the 
        input sequence that occur before the element at which the test no 
        longer passes.        
        """
        predicate = adapt_call(predicate)
        observable = self
        def subscribe(observer):
            running, i = True, 0

            def on_next(value):
                nonlocal running, i
                if running:
                    try:
                        running = predicate(value, i)
                    except Exception as exn:
                        observer.on_error(exn)
                        return
                    else:
                        i += 1
                    
                    if running:
                        observer.on_next(value)
                    else:
                        observer.on_completed()
    
            return observable.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
        
