from rx.observable import Observable
from rx.internal import DisposedException
from rx.disposables import Disposable
from rx.abstractobserver import AbstractObserver

from .anonymoussubject import AnonymousSubject
from .innersubscription import InnerSubscription

class BehaviorSubject(Observable, AbstractObserver):
    """Represents a value that changes over time. Observers can subscribe to 
    the subject to receive the last (or initial) value and all subsequent 
    notifications.
    """
    
    def __init__(self, value):
        """Initializes a new instance of the BehaviorSubject class which 
        creates a subject that caches its last value and starts with the 
        specified value.
        
        Keyword parameters:
        value -- Initial value sent to observers when no other value has been received by the subject yet.
        """
        super(BehaviorSubject, self).__init__(self.subscribe)

        self.value = value
        self.observers = []
        self.is_disposed = False
        self.is_stopped = False
        self.exception = None
    
    def check_disposed(self):
        if self.is_disposed:
            raise DisposedException()
    
    def subscribe(self, observer):
        self.check_disposed()
        if not self.is_stopped:
            self.observers.append(observer)
            observer.on_next(self.value)
            return InnerSubscription(self, observer)
        
        ex = self.exception
        if ex:
            observer.on_error(ex)
        else:
            observer.on_completed()
        
        return Disposable.empty()
    
    def on_completed(self):
        self.check_disposed()
        if not self.is_stopped:
            os = self.observers[:]
            self.is_stopped = True
            for o in os:
                os.on_completed()

            self.observers = []
    
    def on_error(self, error):
        self.check_disposed()
        if not self.is_stopped:
            os = self.observers[:]
            self.is_stopped = True
            self.exception = error

            for o in os:
                o.on_error(error)

            self.observers = []
        
    def on_next(self, value):
        self.check_disposed()
        if not self.is_stopped:
            self.value = value
            os = self.observers[:]
            for o in os:
                o.on_next(value)
    
    def dispose(self):
        self.is_disposed = True
        self.observers = None
        self.value = None
        self.exception = None
    


