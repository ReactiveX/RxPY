import logging
from collections import OrderedDict

from rx import AnonymousObservable, Observable
from rx.internal.utils import add_ref
from rx.internal import noop
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable

log = logging.getLogger("Rx")

class ObservableCoincidence(Observable, metaclass=ObservableMeta):

    def join(self, right, left_duration_selector, right_duration_selector, result_selector):
        """Correlates the elements of two sequences based on overlapping durations.
    
        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_selector -- A function to select the duration (expressed 
            as an observable sequence) of each element of the left observable 
            sequence, used to determine overlap.
        right_duration_selector -- A function to select the duration (expressed 
            as an observable sequence) of each element of the right observable 
            sequence, used to determine overlap.
        result_selector -- A function invoked to compute a result element for 
            any two overlapping elements of the left and right observable 
            sequences. The parameters passed to the function correspond with 
            the elements from the left and right source sequences for which 
            overlap occurs.
        
        Return an observable sequence that contains result elements computed 
        from source elements that have an overlapping duration.
        """   

        left = self

        def subscribe(observer):
            group = CompositeDisposable()
            left_done = [False]
            left_map = OrderedDict()
            left_id = [0]
            right_done = [False]
            right_map = OrderedDict()
            right_id = [0]
            
            def on_next_left(value):
                duration = None
                current_id = left_id[0]
                left_id[0] += 1
                md = SingleAssignmentDisposable()
                
                #log.debug("**** left_map[%s] = %s" % (current_id, value))
                #log.debug(value.get_hash_code())
                
                left_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in left_map:
                        del left_map[current_id]
                    if not len(left_map) and left_done[0]:
                        observer.on_completed()
                
                    return group.remove(md)
                
                try:
                    duration = left_duration_selector(value)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.on_error(exception)
                    return
                
                md.disposable = duration.take(1).subscribe(noop, observer.on_error, lambda: expire())
                values = right_map.values()
                for val in values:
                    try:
                        result = result_selector(value, val)
                    except Exception as exception:
                        log.error("*** Exception: %s" % exception)
                        observer.on_error(exception)
                        return
                    
                    observer.on_next(result)
                
            def on_completed_left():
                left_done[0] = True
                if right_done[0] or not len(left_map):
                    observer.on_completed()
                
            group.add(left.subscribe(on_next_left, observer.on_error, on_completed_left))

            def on_next_right(value):
                duration = None
                current_id = right_id[0]
                right_id[0] += 1
                md = SingleAssignmentDisposable()
                right_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in right_map:
                        del right_map[current_id]
                    if not len(right_map) and right_done[0]:
                        observer.on_completed()
                        
                    return group.remove(md)
                
                try:
                    duration = right_duration_selector(value)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.on_error(exception)
                    return
                
                md.disposable = duration.take(1).subscribe(noop, observer.on_error, lambda: expire())
                values = left_map.values()
                for val in values:
                    try:
                        result = result_selector(val, value)
                    except Exception as exception:
                        log.error("*** Exception: %s" % exception)
                        observer.on_error(exception)
                        return
                    
                    observer.on_next(result)
                
            def on_completed_right():
                right_done[0] = True
                if left_done[0] or not len(right_map):
                    observer.on_completed()
                
            group.add(right.subscribe(on_next_right, observer.on_error, on_completed_right))
            return group
        
        return AnonymousObservable(subscribe)
    
    def group_join(self, right, left_duration_selector, right_duration_selector, result_selector):
        """Correlates the elements of two sequences based on overlapping 
        durations, and groups the results.
     
        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_selector -- A function to select the duration (expressed 
            as an observable sequence) of each element of the left observable 
            sequence, used to determine overlap.
        right_duration_selector -- A function to select the duration (expressed
            as an observable sequence) of each element of the right observable 
            sequence, used to determine overlap.
        result_selector -- A function invoked to compute a result element for 
            any element of the left sequence with overlapping elements from the 
            right observable sequence. The first parameter passed to the 
            function is an element of the left sequence. The second parameter 
            passed to the function is an observable sequence with elements from 
            the right sequence that overlap with the left sequence's element.
    
        Returns an observable sequence that contains result elements computed 
        from source elements that have an overlapping duration.   
        """
        left = self

        def subscribe(observer):
            nothing = lambda _: None
            group = CompositeDisposable()
            r = RefCountDisposable(group)
            left_map = OrderedDict()
            right_map = OrderedDict()
            left_id = 0
            right_id = 0

            def on_next_left(value):
                s = Subject()
                _id = left_id
                left_id += 1
                left_map.add(_id, s)
                
                try:
                    result = result_selector(value, add_ref(s, r))
                except Exception as e:
                    log.error("*** Exception: %s" % e)
                    left_values = left_map.getValues()
                    for left_value in left_values:
                        left_value.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                observer.on_next(result)

                right_values = right_map.getValues()
                for right_value in right_values:
                    s.on_next(right_value)
                
                md = SingleAssignmentDisposable()
                group.add(md)

                def expire():
                    if left_map.remove(_id):
                        s.on_completed()
                    
                    group.remove(md)
                
                try:
                    duration = left_duration_selector(value)
                except Exception as e:
                    left_values = left_map.getValues()
                    for left_value in left_values:
                        left_value.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                def on_error(e):
                    left_values = left_map.getValues()
                    for left_value in left_values:
                        left_value.on_error(e)
                    
                    observer.on_error(e)
                    
                md.disposable = duration.take(1).subscribe(
                    nothing,
                    on_error,
                    expire)
            
            def on_error_left(e):
                left_values = left_map.values()
                for left_value in left_values:
                    left_value.on_error(e)
                
                observer.on_error(e)
                
            group.add(left.subscribe(on_next_left, on_error_left, observer.on_completed))

            def on_next_right(value):
                left_values, i, len
                _id = right_id
                right_id += 1
                right_map.add(id, value)

                md = SingleAssignmentDisposable()
                group.add(md)

                def expire():
                    right_map.remove(id)
                    group.remove(md)
                
                try:
                    duration = right_duration_selector(value)
                except Exception as e:
                    left_values = left_map.getValues()
                    for left_value in left_values:
                        left_value.on_error(e)
                    
                    observer.on_error(e)
                    return
                
                def on_error(e):
                    left_values = left_map.getValues()
                    for left_value in left_map:
                        left_value.on_error(e)
                    
                    observer.on_error(e)
                    
                md.disposable = duration.take(1).subscribe(
                    nothing,
                    on_error,
                    expire)

                left_values = left_map.getValues()
                for left_value in left_values:
                    left_values.on_next(value)
            
            def on_error_right(e):
                left_values = left_map.values()
                for left_value in left_values:
                    left_value.on_error(e)
                
                observer.on_error(e)
            
            group.add(right.subscribe(on_next_right, on_error_right))
            return r
        return AnonymousObservable(subscribe)

    def buffer(self, buffer_openings=None, closing_selector=None, buffer_closing_selector=None):
        """Projects each element of an observable sequence into zero or more 
        buffers.
         
        Keyword arguments:
        buffer_openings -- Observable sequence whose elements denote the 
            creation of windows.
        closing_selector -- Or, a function invoked to define the boundaries of 
            the produced windows (a window is started when the previous one is 
            closed, resulting in non-overlapping windows).
        buffer_closing_selector -- [optional] A function invoked to define the 
            closing of each produced window. If a closing selector function is 
            specified for the first parameter, self parameter is ignored.
        
        Returns an observable sequence of windows.    
        """
        if buffer_openings and not buffer_closing_selector:
            return self.observable_window_with_bounaries(buffer_openings).select_many(lambda item: item.to_array())
        
        if closing_selector:
            return self.observable_window_with_closing_selector(closing_selector).select_many(lambda item: item.to_array())
        else:
            return self.observable_window_with_openings(closing_selector, buffer_closing_selector).select_many(lambda item: item.to_array())
    
    
    def window(self, window_openings=None, closing_selector=None, window_closing_selector=None):
        """Projects each element of an observable sequence into zero or more 
        windows.
         
        Keyword arguments: 
        window_openings -- Observable sequence whose elements denote the 
            creation of windows.
        closing_selector -- Or, a function invoked to define the boundaries of 
            the produced windows (a window is started when the previous one is 
            closed, resulting in non-overlapping windows).
        window_closing_selector -- [Optional] A function invoked to define the 
            closing of each produced window. If a closing selector function is 
            specified for the first parameter, self parameter is ignored.
        
        Returns an observable sequence of windows.
        """
        if window_openings and not window_closing_selector:
            return observable_window_with_bounaries(self, window_ppenings_or_closingSelector)
        
        if closing_selector:
            return self.observable_window_with_closing_selector(closingSelector)
        else:
            return self.observable_window_with_openings(window_openings, window_closing_selector)
    
    def observable_window_with_openings(window_openings, window_closing_selector):
        return self.window_openings.group_join(window_closing_selector, lambda: Observable.empty(), lambda _, window: window)
    
    def observable_window_with_bounaries(self, window_boundaries):
        source = self

        def subscribe(observer):
            window = Subject()
            d = CompositeDisposable()
            r = RefCountDisposable(d)

            observer.on_next(add_ref(window, r))

            def on_next_window(x):
                window.on_next(x)
            
            def on_error(err):
                window.on_error(err)
                observer.on_error(err)
            
            def on_completed():
                window.on_completed()
                observer.on_completed()

            d.add(source.subscribe(on_next_window, on_error, on_completed))

            def on_next_observer(w):
                window.on_completed()
                window = Subject()
                observer.on_next(add_ref(window, r))
            
            d.add(window_boundaries.subscribe(on_next_observer, on_error, on_copleted))
            return r
        return AnonymousObservable(subscribe)
    

    def observable_window_with_closing_selector(self, window_closing_selector):
        source = self

        def subscribe(observer):
            m = SerialDisposable()
            d = CompositeDisposable(m)
            r = RefCountDisposable(d)
            window = Subject()
            
            observer.on_next(add_ref(window, r))

            def on_next(x):
                window.on_next(x)
            
            def on_error(ex):
                window.on_error(ex)
                observer.on_error(ex)
            
            def on_completed():
                window.on_completed()
                observer.on_completed()
            
            d.add(source.subscribe(on_next, on_error, on_completed))
            
            def create_window_close():
                try:
                    window_close = window_closing_selector()
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.on_error(exception)
                    return
                
                def on_completed():
                    window.on_completed()
                    window = Subject()
                    observer.on_next(add_ref(window, r))
                    create_window_close()
                
                m1 = SingleAssignmentDisposable()
                m.disposable(m1)
                m1.disposable(window_close.take(1).subscribe(noop, on_error, on_completed))
            
            create_window_close()
            return r        
        return AnonymousObservable(subscribe)
