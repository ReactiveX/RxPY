from rx import Observable
from rx.internal.basic import object_is_disposed

from .innersubscription import InnerSubscription

class Subject(Observable):
    """Represents an object that is both an observable sequence as well as an observer. Each notification is broadcasted to all subscribed observers."""

    def __init__(self):
        super(Subject, self).__init__(self.subscribe)
        
        self.is_disposed = False
        self.is_stopped = False
        self.observers = []

    def check_disposed(self):
        if self.is_disposed:
            raise Exception(object_is_disposed)

    def subscribe(self, observer):
        self.check_disposed()
        if not self.is_stopped:
            self.observers.append(observer)
            return InnerSubscription(self, observer)
        
        if self.exception:
            observer.on_error(self.exception)
            return Disposable.empty()
        
        observer.on_completed()
        return Disposable.empty()
    
    def on_completed(self):
        """Notifies all subscribed observers of the end of the sequence."""
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True

            for os in self.observers:
                os.on_completed()

            self.observers = []

    def on_error(self, exception):
        """Notifies all subscribed observers with the exception.
        
        Keyword arguments:
        error -- The exception to send to all subscribed observers.
        """
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            self.exception = exception
            for os in self.observers:
                os.on_error(exception)

            self.observers = []

    def on_next(self, value):
        """Notifies all subscribed observers with the value.
        
        Keyword arguments:
        value -- The value to send to all subscribed observers.
        """
        self.check_disposed()
        if not self.is_stopped:
            for os in self.observers:
                os.on_next(value)

    def dispose(self):
        """Unsubscribe all observers and release resources."""
        
        self.is_disposed = True
        self.observers = None
    
    @classmethod
    def create(cls, observer, observable):
        return AnonymousSubject(observer, observable)
    