from rx.internal import noop, default_error

from .abstractobserver import AbstractObserver

class Observer(AbstractObserver):
    def __init__(self, on_next=None, on_error=None, on_completed=None):
        super(Observer, self).__init__()

        self._on_next = on_next or noop
        self._on_error = on_error or default_error
        self._on_completed = on_completed or noop

    def next(self, value):
        self._on_next(value)

    def completed(self):
        self._on_completed()

    def error(self, ex):
        self._on_error(ex)

    @classmethod
    def from_notifier(cls, handler):
        def on_next(x):
            return handler(notification_create_on_next(x))
        def on_error(ex):
            return handler(notification_create_on_error(exception))
        def on_completed():
            return handler(notification_create_on_completed())

        return cls(on_next, on_error, on_completed)
 
    def to_notifier(self):
        observer = self

        def func(n):
            return n.accept(observer)
        
        return func

    def checked(self):
        return CheckedObserver(self)

    #def as_observer():
    #    return AnonymousObserver(self.on_next, this.on_error, on_completed)
