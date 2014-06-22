import logging
from collections import OrderedDict

from rx import AnonymousObservable, Observable
from rx.internal.utils import add_ref
from rx.internal import noop
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable, RefCountDisposable
from rx.subjects import Subject

log = logging.getLogger("Rx")

class ObservableWindow(Observable, metaclass=ObservableMeta):
    def window(self, window_openings=None, closing_selector=None, window_closing_selector=None):
        """Projects each element of an observable sequence into zero or more 
        windows.
         
        Keyword arguments: 
        window_openings -- Observable sequence whose elements denote the 
            creation of windows.
        closing_selector -- A function invoked to define the boundaries of 
            the produced windows (a window is started when the previous one is 
            closed, resulting in non-overlapping windows).
        window_closing_selector -- [Optional] A function invoked to define the 
            closing of each produced window. If a closing selector function is 
            specified for the first parameter, self parameter is ignored.
        
        Returns an observable sequence of windows.
        """
        if window_openings and not window_closing_selector:
            return self.observable_window_with_bounaries(window_openings)
        
        if closing_selector:
            return self.observable_window_with_closing_selector(closing_selector)
        else:
            return self.observable_window_with_openings(window_openings, window_closing_selector)
    
    def observable_window_with_openings(self, window_openings, window_closing_selector):
        return window_openings.group_join(window_closing_selector, lambda: Observable.empty(), lambda _, window: window)
    
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
            
            d.add(window_boundaries.subscribe(on_next_observer, on_error, on_completed))
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
                    nonlocal window
                    
                    window.on_completed()
                    window = Subject()
                    observer.on_next(add_ref(window, r))
                    create_window_close()
                
                m1 = SingleAssignmentDisposable()
                m.disposable = m1
                m1.disposable = window_close.take(1).subscribe(noop, on_error, on_completed)
            
            create_window_close()
            return r        
        return AnonymousObservable(subscribe)
