import sys
from datetime import timedelta

from rx.observable import Observable
from rx.internal import DisposedException
from rx.disposables import Disposable
from rx.abstractobserver import AbstractObserver
from rx.concurrency import current_thread_scheduler
from rx.scheduledobserver import ScheduledObserver

from .anonymoussubject import AnonymousSubject
from .innersubscription import InnerSubscription

class RemovableDisposable(object):
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer

    def dispose(self):
        self.observer.dispose()
        if not self.subject.is_disposed and self.observer in self.subject.observers:
            self.subject.observers.remove(self.observer)
            
# Replay Subject
class ReplaySubject(Observable, AbstractObserver):
    """Represents an object that is both an observable sequence as well as an 
    observer. Each notification is broadcasted to all subscribed and future 
    observers, subject to buffer trimming policies.
    """ 
    
    def __init__(self, buffer_size=None, window=None, scheduler=None):
        """Initializes a new instance of the ReplaySubject class with the 
        specified buffer size, window and scheduler.
     
        Keyword arguments:
        buffer_size -- [Optional] Maximum element count of the replay buffer.
        window [Optional] -- Maximum time length of the replay buffer.
        scheduler -- [Optional] Scheduler the observers are invoked on.
        """
    
        self.buffer_size = sys.maxsize if buffer_size is None else buffer_size
        self.window = timedelta.max if window is None else window
        if not isinstance(self.window, timedelta):
            self.window = timedelta(milliseconds=self.window)
        self.scheduler = scheduler or current_thread_scheduler
        self.q = []
        self.observers = []
        self.is_stopped = False
        self.is_disposed = False
        self.has_error = False
        self.error = None

        super(ReplaySubject, self).__init__(self.__subscribe)

    def check_disposed(self):
        if self.is_disposed:
            raise DisposedException()

    def __subscribe(self, observer):
        so = ScheduledObserver(self.scheduler, observer)
        subscription = RemovableDisposable(self, so)
        self.check_disposed()
        self._trim(self.scheduler.now())
        self.observers.append(so)

        n = len(self.q)

        for item in self.q:
            so.on_next(item['value'])

        if self.has_error:
            n += 1
            so.on_error(self.error)
        elif self.is_stopped:
            n += 1
            so.on_completed()

        so.ensure_active() # n)
        return subscription
    
    def _trim(self, now):
        while len(self.q) > self.buffer_size:
            self.q.pop(0)
        
        while len(self.q) > 0 and (now - self.q[0]['interval']) > self.window:
            self.q.pop(0)

    def on_next(self, value):
        self.check_disposed()
        if not self.is_stopped:
            now = self.scheduler.now()
            self.q.append(dict(interval=now, value=value))
            self._trim(now)

            for observer in self.observers:
                observer.on_next(value)
                observer.ensure_active()
    
    def on_error(self, error):
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            self.error = error
            self.has_error = True
            now = self.scheduler.now()
            self._trim(now)
            
            for observer in self.observers:
                observer.on_error(error)
                observer.ensure_active()
            
            self.observers = []
        
    def on_completed(self):
        self.check_disposed()
        if not self.is_stopped:
            self.is_stopped = True
            now = self.scheduler.now()
            self._trim(now)
            for observer in self.observers:
                observer.on_completed()
                observer.ensure_active()
            
            self.observers = []
        
    def dispose(self):
        self.is_disposed = True
        self.observers = None
    
