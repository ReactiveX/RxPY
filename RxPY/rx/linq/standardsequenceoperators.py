from rx import Observable, AnonymousObservable

from inspect import getargspec, getargvalues 

def adapt_call(func):
    """Adapts func from taking 2 params to only taking 1 param"""
    def func1(arg1, arg2):
        return func(arg1)

    func_wrapped = func
    argnames, varargs, kwargs = getargspec(func)[:3]
    if len(argnames) == 1 and not varargs and not kwargs:
        func_wrapped = func1
    
    return func_wrapped

class ObservableLinq(object):
    # Observable.select extension metho
    def select(self, selector):
        """Projects each element of an observable sequence into a new form by incorporating the element's index.
        
        1 - source.select(lambda value: value * value)
        2 - source.select(lambda value, index: value * value + index)
        
        Keyword arguments:
        selector -- A transform function to apply to each source element; the second parameter of the function represents the index of the source element.
        
        Returns an observable sequence whose elements are the result of invoking the transform function on each element of source.
        """
        #print ("Observable:select(%s)" % selector)

        selector = adapt_call(selector)        

        def subscribe(observer):
            count = 0

            def on_next(value):
                nonlocal count
                result = None
                try:
                    result = selector(value, count)
                except Exception as err:
                    observer.on_error(err)
                else:
                    count += 1
                    observer.on_next(result)

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    def take(self, count, scheduler=None):
        if count < 0:
            raise Exception(argumentOutOfRange)
        
        if not count:
            return Observable.empty(scheduler)
        
        def subscribe(observer):
            nonlocal count
            remaining = count

            def on_next(x):
                if remaining > 0:
                    remaining -= 1
                    observer.on_next(x)
                    if not remaining:
                        observer.on_completed()

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    def where(self, predicate):
        """Filters the elements of an observable sequence based on a predicate by incorporating the element's index.
        
        1 - source.where(lambda value: value < 10)
        2 - source.where(lambda value, index: value < 10 or index < 10)
        
        Keyword arguments:
        predicate -- A function to test each source element for a conditio; the second parameter of the function represents the index of the source element.
        
        Returns an observable sequence that contains elements from the input sequence that satisfy the condition.
        """
        predicate = adapt_call(predicate)
        parent = self
        
        def subscribe(observer):
            count = 0
            def on_next(value):
                nonlocal count
                should_run = False
                try:
                    should_run = predicate(value, count)
                except Exception as ex:
                    observer.on_error(ex)
                    return
                else:
                    count += 1
                
                if should_run:
                    observer.on_next(value)
                
            return parent.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

# Stitch methods into the main Observable "God" object
Observable.select = ObservableLinq.select
Observable.where = ObservableLinq.where
Observable.take = ObservableLinq.take
