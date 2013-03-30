from rx import Observable
from rx.internal.basic import object_is_disposed

class Subject(Observable):
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
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True

            for os in self.observers:
                os.on_completed()

            self.observers = []

    def on_error(self, exception):
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            self.exception = exception
            for os in self.observers:
                os.on_error(exception)

            self.observers = []

    def on_next(self, value):
        self.check_disposed()
        if not self.is_stopped:
            for os in self.observers:
                os.on_next(value)

    def dispose(self):
        self.is_disposed = True
        self.observers = None
    
    @classmethod
    def create(cls, observer, observable):
        return AnonymousSubject(observer, observable)
    