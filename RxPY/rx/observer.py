from rx.internal import noop, default_error

from .abstractobserver import AbstractObserver
from .anonymousobserver import AnonymousObserver

class Observer(AbstractObserver):
    """Supports push-style iteration over an observable sequence."""

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
 
    def to_notifier(self):
        """Creates a notification callback from an observer.
        
        Returns the action that forwards its input notification to the underlying observer.
        """
        observer = self

        def func(notifier):
            return notifier.accept(observer)
        return func

    def as_observer(self):
        """Hides the identity of an observer.
        
        Returns an observer that hides the identity of the specified observer.
        """
        return AnonymousObserver(self.on_next, self.on_error, self.on_completed)
