from datetime import timedelta

from rx.concurrency import VirtualTimeScheduler

from .coldobservable import ColdObservable
from .hotobservable import HotObservable
from .mockobserver import MockObserver

class TestScheduler(VirtualTimeScheduler):
    def __init__(self):
        def comparer(a, b):
            return a - b
        super(TestScheduler, self).__init__(0, comparer)

    def schedule_absolute(self, duetime, action, state=None):
        if isinstance(duetime, int):
            duetime =  self.clock + timedelta(duetime)

        if duetime <= self.clock:
            duetime = self.clock + timedelta(1)
        
        return super(TestScheduler, self).schedule_absolute(duetime, action, state)
    
    def add(self, absolute, relative):
        return absolute + relative
    
    def to_datetime_offset(absolute):
        return absolute #new Date(absolute).getTime()
    
    def to_relative(self, timespan):
        return timespan
    
    def start_with_timing(self, create, created, subscribed, disposed):
        server = self.create()

        def action1(scheduler, state):
            source = create()
            return Disposable.empty()

        self.schedule_absolute(created, action1)

        def action2(scheduler, state):
            subscription = source.subscribe(observer)
            return Disposable.empty()

        this.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            subscription.dispose()
            return DisposableEmpty()

        self.schedule_absolute(disposed, action3)
        self.start()
        return observer

    def start_with_dispose(self, create, disposed):
        return self.start_with_timing(create, ReactiveTest.created, ReactiveTest.subscribed, disposed)
    
    def start_with_create(self, create):
        return self.start_with_timing(create, ReactiveTest.created, ReactiveTest.subscribed, ReactiveTest.disposed)
    
    def create_hot_observable(self, *args):
        messages = list(args)
        return HotObservable(self, messages)

    def create_cold_observable(self, *args):
        messages = list(args)
        return ColdObservable(self, messages)
    
    @classmethod
    def create_observer(cls):
        return MockObserver(cls())
    
