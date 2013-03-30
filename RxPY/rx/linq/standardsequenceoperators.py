from rx import Observable, AnonymousObservable

from inspect import getargspec, getargvalues 

def adapt_call(func, args, kw, start=0): 
    argnames, varargs, kwargs = getargspec(func)[:3] 
    del argnames[:start] 
    if kwargs in (None, "_decorator__kwargs"): 
        seq = [key for key in kw if key not in argnames]
        for key in seq: 
            kw_.pop(key, None) 
    if varargs in (None, "_decorator__varargs"): 
        args = args[:len(argnames)] 
    for n, key in enumerate(argnames): 
        if key in kw: 
            args = args[:n] 
            break 
    return args, kw 

class ObservableLinq(object):
    # Observable.select extension metho
    def select(self, selector):
        # <summary>
        # Projects each element of an observable sequence into a new form by incorporating the element's index.
        # &#10;
        # &#10;1 - source.select(function (value) { return value * value; });
        # &#10;2 - source.select(function (value, index) { return value * value + index; });
        # </summary>
        # <param name="selector">A transform function to apply to each source element; the second parameter of the function represents the index of the source element.</param>
        # <returns>An observable sequence whose elements are the result of invoking the transform function on each element of source.</returns>        

        #print ("Observable:select(%s)" % selector)
        
        # Selector may or may not take a count parameter. We adapt our call accordingly
        def selector_no_count(value, count):
            return selector(value)

        argnames, varargs, kwargs = getargspec(selector)[:3]
        if len(argnames) == 1 and not varargs and not kwargs:
            selector_wrapped = selector_no_count
        else:
            selector_wrapped = selector

        def subscribe(observer):
            count = 0

            def on_next(value):
                nonlocal count
                result = None
                try:
                    result = selector_wrapped(value, count)
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

# Stitch methods into the main Observable "God" object
Observable.select = ObservableLinq.select
Observable.take = ObservableLinq.take
