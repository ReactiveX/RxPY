import six
from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.subjects import Subject
from rx.observable import ObservableMeta
from rx.disposables import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.internal.basic import default_key_serializer, identity

from rx.linq.groupedobservable import GroupedObservable

@add_metaclass(ObservableMeta)
class ObservableGroupByUntil(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def group_by_until(self, key_selector, element_selector, duration_selector, key_serializer=None):
        """Groups the elements of an observable sequence according to a 
        specified key selector function. A duration selector function is used
        to control the lifetime of groups. When a group expires, it receives 
        an OnCompleted notification. When a new element with the same key value
        as a reclaimed group occurs, the group will be reborn with a new 
        lifetime request.
        
        1 - observable.group_by_until(function (x) { return x.id; }, null,  function () { return Rx.Observable.never(); });
        2 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; },  function () { return Rx.Observable.never(); });
        3 - observable.group_by(function (x) { return x.id; }), function (x) { return x.name; },  function () { return Rx.Observable.never(); }, function (x) { return x.toString(); });
        
        Keyword arguments:
        key_selector -- A function to extract the key for each element.
        duration_selector -- A function to signal the expiration of a group.
        key_serializer -- [Optional] Used to serialize the given object into a 
            string for object comparison.
        
        Returns a sequence of observable groups, each of which corresponds to 
        a unique key value, containing all elements that share that same key 
        value. If a group's lifetime expires, a new group with the same key 
        value can be created once an element with such a key value is 
        encoutered.
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
                    for w in six.itervalues(mapping):
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
                    for w in six.itervalues(mapping):
                        w.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                if fire_new_map_entry:
                    group = GroupedObservable(key, writer, ref_count_disposable)
                    duration_group = GroupedObservable(key, writer)
                    try:
                        duration = duration_selector(duration_group)
                    except Exception as e:
                        for w in six.itervalues(mapping):
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
                        for wr in six.itervalues(mapping):
                            wr.on_error(exn)
                        observer.on_error(exn)

                    def on_completed():
                        expire()

                    md.disposable = duration.take(1).subscribe(on_next, on_error, on_completed)
                
                try:
                    element = element_selector(x)
                except Exception as e:
                    for w in six.itervalues(mapping):
                        w.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                writer.on_next(element)
            
            def on_error(ex):
                for w in six.itervalues(mapping):
                    w.on_error(ex)
                
                observer.on_error(ex)
            
            def on_completed():
                for w in six.itervalues(mapping):
                    w.on_completed()
                
                observer.on_completed()
            
            group_disposable.add(source.subscribe(on_next, on_error, on_completed))
            return ref_count_disposable
        return AnonymousObservable(subscribe)
