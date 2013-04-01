from datetime import timedelta

from rx.concurrency import VirtualTimeScheduler
from rx.disposables import Disposable

from .coldobservable import ColdObservable
from .hotobservable import HotObservable
from .mockobserver import MockObserver
from .reactivetest import ReactiveTest

class TestScheduler(VirtualTimeScheduler):
    """Virtual time scheduler used for testing applications and libraries 
    built using Reactive Extensions."""

    def __init__(self):
        def comparer(a, b):
            return a - b
        super(TestScheduler, self).__init__(0, comparer)

    def schedule_absolute(self, duetime, action, state=None):
        #print ("TestScheduler:schedule_absolute(%s)", duetime)
        """Schedules an action to be executed at the specified virtual time.
        
        Keyword arguments:
        dueime -- Absolute virtual time at which to execute the action.
        action -- Action to be executed.
        state -- State passed to the action to be executed.
        
        Returns disposable object used to cancel the scheduled action (best effort).
        """
        if duetime <= self.clock:
            duetime = self.clock + 1
        
        return super(TestScheduler, self).schedule_absolute(duetime, action, state)
    
    def add(self, absolute, relative):
        return absolute + relative
    
    @classmethod
    def to_datetime_offset(cls, absolute):
        """Converts the absolute virtual time value to a DateTimeOffset value.
        
        Keyword arguments:
        absolute -- Absolute virtual time value to convert.
        
        Returns corresponding DateTimeOffset value.
        """
            
        return timedelta(microseconds=absolute)
    
    @classmethod
    def to_relative(cls, timespan):
        return timespan
    
    def start_with_timing(self, create, created, subscribed, disposed):
        """Starts the test scheduler and uses the specified virtual times to 
        invoke the factory function, subscribe to the resulting sequence, and
        dispose the subscription.
        
        Keyword arguments:
        create -- Factory method to create an observable sequence.
        created -- Virtual time at which to invoke the factory to create an observable sequence.
        subscribed -- Virtual time at which to subscribe to the created observable sequence.
        disposed -- Virtual time at which to dispose the subscription.
        
        Returns Observer with timestamped recordings of notification messages 
        that were received during the virtual time window when the subscription
        to the source sequence was active.
        """
        observer = self.create_observer()
        subscription = None
        source = None

        def action1(scheduler, state):
            nonlocal source
            source = create()
            return Disposable.empty()
        self.schedule_absolute(created, action1)

        def action2(scheduler, state):
            #print ("action2()")
            nonlocal subscription
            subscription = source.subscribe(observer)
            return Disposable.empty()
        self.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            #print ("action3()")
            subscription.dispose()
            return Disposable.empty()
        self.schedule_absolute(disposed, action3)

        self.start()
        return observer

    def start_with_dispose(self, create, disposed):
        """Starts the test scheduler and uses the specified virtual time to 
        dispose the subscription to the sequence obtained through the factory
        function. Default virtual times are used for factory invocation and 
        sequence subscription.
        
        Keyword arguments:
        create -- Factory method to create an observable sequence.
        disposed -- Virtual time at which to dispose the subscription.
        
        Returns observer with timestamped recordings of notification messages 
        that were received during the virtual time window when the subscription
        to the source sequence was active.
        """
            
        return self.start_with_timing(create, ReactiveTest.created, ReactiveTest.subscribed, disposed)
    
    def start_with_create(self, create):
        """Starts the test scheduler and uses default virtual times to invoke
        the factory function, to subscribe to the resulting sequence, and to 
        dispose the subscription.
        
        Keyword arguments:
        create -- Factory method to create an observable sequence.
        
        Returns observer with timestamped recordings of notification messages 
        that were received during the virtual time window when the subscription
        to the source sequence was active.
        """
        return self.start_with_timing(create, ReactiveTest.created, ReactiveTest.subscribed, ReactiveTest.disposed)
    
    def create_hot_observable(self, *args):
        """Creates a hot observable using the specified timestamped 
        notification messages either as an array or arguments.
        
        Keyword arguments:
        messages -- Notifications to surface through the created sequence at 
            their specified absolute virtual times.
        
        Returns hot observable sequence that can be used to assert the timing 
        of subscriptions and notifications.
        """
        messages = list(args)
        return HotObservable(self, messages)

    def create_cold_observable(self, *args):
        """Creates a cold observable using the specified timestamped notification messages either as an array or arguments.
        
        Keyword arguments:
        messages -- Notifications to surface through the created sequence at their specified virtual time offsets from the sequence subscription time.
        
        Returns cold observable sequence that can be used to assert the timing of subscriptions and notifications.
        """
        messages = list(args)
        return ColdObservable(self, messages)
    
    def create_observer(self):
        """Creates an observer that records received notification messages and timestamps those. Return an Observer that can be used to assert the timing of received notifications.
        """
        return MockObserver(self)
    
