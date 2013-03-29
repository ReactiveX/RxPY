import types

from .anonymousobservable import AnonymousObservable

# Notifications
class Notification(object):
    def __init__(self):
        self.has_value = False
    
    def accept(self, on_next, on_error=None, on_completed=None):
        """Invokes the delegate corresponding to the notification or an observer and returns the produced result. 
        Returns result produced by the observation.
        
        1 - notification.accept(observer)
        2 - notification.accept(on_next, on_error, on_completed)
        
        Keyword arguments:
        on_next -- Delegate to invoke for an OnNext notification.
        on_error -- [Optional] Delegate to invoke for an OnError notification.
        on_completed -- [Optional] Delegate to invoke for an OnCompleted notification.
        """
        if type(on_next) == types.FunctionType:
            return self._accept(on_next, on_error, on_completed)
        else:
            return self._accept_observable(on_next)
    
    def to_observable(self, scheduler=None):
        """Returns an observable sequence with a single notification, using the specified scheduler, else the immediate scheduler. The returned observable sequence surfaces the behavior of the notification upon subscription.

        Keyword arguments:
        scheduler -- [Optional] Scheduler to send out the notification calls on.
        """
        notification = self
        scheduler = scheduler or ImmediateScheduler()

        def subscribe(observer):
            def action(scheduler, state):
                notification._accept_bservable(observer)
                if notification.kind == 'N':
                    observer.on_completed()
                
            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    def equals(self, other):
        """Indicates whether this instance and a specified object are equal."""
        other_string = '' if not other else str(other)
        return str(self) == other_string

    def __eq__(self, other):
        return self.equals(other)
    
class ON(Notification):
    def __init__(self, value):
        self.value = value
        self.has_value = True
        self.kind = 'N'

    def _accept(self, on_next):
        return on_next(self.value)
    
    def _accept_observable(self, observer):
        return observer.on_next(self.value)
    
    def __str__(self):
        return "OnNext(%s)" % self.value
    
class OE(Notification):
    def __init__(self, exception):
        self.exception = exception
        self.kind = 'E'

    def _accept(on_next, on_error):
        return on_error(self.exception)
    
    def _accept_observable(self, observer):
        return observer.on_error(self.exception)
    
    def __str__(self):
        return "OnError(%s)" % self.exception

class OC(Notification):
    def __init__(self):
        self.kind = 'C'

    def _accept(self, on_next, on_error, on_completed):
        return on_completed()
    
    def _accept_observable(self, observer):
        return observer.on_completed()
    
    def __str__(self):
        return "OnCompleted()"
    