from inspect import getargspec, getargvalues 

from rx import Observable, AnonymousObservable
from rx.subjects import Subject
from rx.disposables import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.internal.basic import default_key_serializer, identity

from .groupedobservable import GroupedObservable

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

    def group_by(self, key_selector, element_selector=None, key_serializer=None):
        """Groups the elements of an observable sequence according to a specified key selector function and comparer and selects the resulting elements by using a specified function.
        
        1 - observable.group_by(function (x) { return x.id; });
        2 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; });
        3 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; }, function (x) { return x.toString(); });
        
        Keyword arguments:
        key_selector -- A function to extract the key for each element.</param>
        element_selector -- [Optional] A function to map each source element to an element in an observable group.</param>
        key_serializer -- [Optional] Used to serialize the given object into a string for object comparison.</param>
        
        Returns a sequence of observable groups, each of which corresponds to a unique key value, containing all elements that share that same key value.</returns>        
        """

        def duration_selector(x):
            return Observable.never()

        return self.group_by_until(key_selector, element_selector, duration_selector, key_serializer)

    def group_by_until(self, key_selector, element_selector, duration_selector, key_serializer=None):
        """Groups the elements of an observable sequence according to a specified key selector function.
        A duration selector function is used to control the lifetime of groups. When a group expires, it receives an OnCompleted notification. When a new element with the same
        key value as a reclaimed group occurs, the group will be reborn with a new lifetime request.
        
        1 - observable.group_by_until(function (x) { return x.id; }, null,  function () { return Rx.Observable.never(); });
        2 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; },  function () { return Rx.Observable.never(); });
        3 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; },  function () { return Rx.Observable.never(); }, function (x) { return x.toString(); });
        
        Keyword arguments:
        key_selector -- A function to extract the key for each element.
        duration_selector -- A function to signal the expiration of a group.
        key_serializer -- [Optional] Used to serialize the given object into a string for object comparison.
        
        Returns a sequence of observable groups, each of which corresponds to a unique key value, containing all elements that share that same key value.
        If a group's lifetime expires, a new group with the same key value can be created once an element with such a key value is encoutered.
        """      

        source = self
        element_selector = element_selector or identity
        key_serializer = key_serializer or default_key_serializer
        
        def subscribe(observer):
            mapping = {}
            group_disposable = CompositeDisposable()
            ref_count_disposable = RefCountDisposable(group_disposable)
            
            def on_next(x):
                writer = None
                element = None
                duration = None
                key = None
                
                try:
                    key = key_selector(x)
                except Exception as e:
                    for w in mapping.values():
                        w.on_error(e)
                    
                    observer.on_error(e)
                    return
                else:
                    serialized_key = key_serializer(key)
                
                fire_new_map_entry = False
                try:
                    writer = mapping.get(serialized_key)
                    if not writer:
                        writer = Subject()
                        mapping[serialized_key] = writer
                        fire_new_map_entry = True
                    
                except Exception as e:
                    print("Exception ********************", e)
                    for w in mapping.values():
                        w.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                if fire_new_map_entry:
                    group = GroupedObservable(key, writer, ref_count_disposable)
                    duration_group = GroupedObservable(key, writer)
                    try:
                        duration = duration_selector(duration_group)
                    except Exception as e:
                        print ("Exception *****************", e)
                        for w in mapping.values():
                            w.on_error(e)
                        
                        observer.on_error(e)
                        return
                    
                    observer.on_next(group)
                    md = SingleAssignmentDisposable()
                    group_disposable.add(md)
                    
                    def expire():
                        if mapping[serialized_key]:
                            del mapping[serialized_key]
                            writer.on_completed()
                        
                        group_disposable.remove(md)
                    
                    def on_next(value):
                        pass

                    def on_error(exn):
                        print ("on_error()", exn)
                        for w in mapping.values():
                            w.on_error(exn)
                        observer.on_error(exn)

                    def on_completed():
                        expire()

                    md.set_disposable(duration.take(1).subscribe(on_next, on_error, on_completed))
                
                try:
                    element = element_selector(x)
                except Exception as e:
                    print("Exception ********************", e)
                    for w in mapping.values():
                        w.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                writer.on_next(element)
            
            def on_error(ex):
                print ("on_error(%s)" % ex)
                for w in mapping.values():
                    w.on_error(ex)
                
                observer.on_error(ex)
            
            def on_completed():
                for w in mapping.values():
                    w.on_completed()
                
                observer.on_completed()
            
            group_disposable.add(source.subscribe(on_next, on_error, on_completed))
            return ref_count_disposable

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
Observable.group_by = ObservableLinq.group_by
Observable.group_by_until = ObservableLinq.group_by_until
Observable.where = ObservableLinq.where
Observable.take = ObservableLinq.take
