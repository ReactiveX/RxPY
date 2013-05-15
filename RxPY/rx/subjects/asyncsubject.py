from rx.observable import Observable
from rx.internal import DisposedException
from rx.disposables import Disposable
from rx.abstractobserver import AbstractObserver

from .innersubscription import InnerSubscription

class AsyncSubject(Observable, AbstractObserver):
    """Represents the result of an asynchronous operation. The last value 
    before the on_completed notification, or the error received through on_error, 
    is sent to all subscribed observers.
    """  

    def subscribe(self, observer):
        self.check_disposed()
        if not self.is_stopped:
            self.observers.append(observer)
            return InnerSubscription(self, observer)
        
        ex = self.exception
        hv = self.has_value
        v = self.value
        if ex:
            observer.on_error(ex)
        elif hv:
            observer.on_next(v)
            observer.on_completed()
        else:
            observer.on_completed()
        
        return disposableEmpty
    
    def __init__(self):
        """Creates a subject that can only receive one value and that value is 
        cached for all future observations.
        """
    
        super(AsyncSubject, self).__init__(self.subscribe)

        self.is_disposed = False
        self.is_stopped = False
        self.value = None
        self.has_value = False
        self.observers = []
        self.exception = None
    

    def on_completed(self):
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            v = self.value
            hv = self.has_value

            if hv:
                for o in self.observers:
                    o.on_next(v)
                    o.on_completed()
            else:
                for o in self.observers:
                    o.on_completed()
                
            self.observers = []
        
    def on_error(self, exception):
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            self.exception = exception

            for o in self.observers:
                o.on_error(exception)
            
            self.observers = []
    
    def on_next(self, value):
        self.check_disposed()
        if not self.is_stopped:
            self.value = value
            self.has_value = True
        
    def dispose(self):
        self.is_disposed = True
        self.observers = None
        self.exception = None
        self.value = None

