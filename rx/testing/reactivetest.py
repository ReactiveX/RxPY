import types

from rx.notification import Notification, ON, OE, OC
from .recorded import Recorded
from .subscription import Subscription

# New predicate tests
class OnNextPredicate(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def equals(self, other):
        if other == self:
            return True
        if other == None:
            return False
        if other.kind != 'N': 
            return False
        return self.predicate(other.value)

class OnErrorPredicate(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def equals(self, other):
        if other == self:
            return True
        if other == None: 
            return False
        if other.kind != 'E': 
            return False
        return self.predicate(other.exception)

class ReactiveTest(object):
    created = 100
    subscribed = 200
    disposed = 1000

    @classmethod
    def on_next(cls, ticks, value):
        if type(value) == types.FunctionType:
            return Recorded(ticks, OnNextPredicate(value))
        
        return Recorded(ticks, ON(value))
    
    @classmethod
    def on_error(cls, ticks, exception):
        if type(exception) == types.FunctionType:
            return Recorded(ticks, OnErrorPredicate(exception))
        
        return Recorded(ticks, OE(exception))
    
    @classmethod
    def on_completed(cls, ticks):
        return Recorded(ticks, OC())
    
    @classmethod
    def subscribe(cls, start, end):
        return Subscription(start, end)

