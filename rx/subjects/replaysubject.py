import sys
from datetime import timedelta

from rx import config
from rx.core import Observer, Observable
from rx.internal import DisposedException
from rx.concurrency import current_thread_scheduler
from rx.core.scheduledobserver import ScheduledObserver


class RemovableDisposable(object):
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer

    def dispose(self):
        self.observer.dispose()
        if not self.subject.is_disposed and self.observer in self.subject.observers:
            self.subject.observers.remove(self.observer)


class ReplaySubject(Observable, Observer):
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
        self.scheduler = scheduler or current_thread_scheduler
        self.window = timedelta.max if window is None else self.scheduler.to_timedelta(window)
        self.queue = []
        self.observers = []
        self.is_stopped = False
        self.is_disposed = False
        self.has_error = False
        self.error = None

        self.lock = config["concurrency"].RLock()

        super(ReplaySubject, self).__init__()

    def check_disposed(self):
        if self.is_disposed:
            raise DisposedException()

    def _subscribe_core(self, observer, scheduler=None):
        so = ScheduledObserver(self.scheduler, observer)
        subscription = RemovableDisposable(self, so)

        with self.lock:
            self.check_disposed()
            self._trim(self.scheduler.now)
            self.observers.append(so)

            for item in self.queue:
                so.send(item['value'])

            if self.has_error:
                so.throw(self.error)
            elif self.is_stopped:
                so.close()

        so.ensure_active()
        return subscription

    def _trim(self, now):
        while len(self.queue) > self.buffer_size:
            self.queue.pop(0)

        while self.queue and (now - self.queue[0]['interval']) > self.window:
            self.queue.pop(0)

    def send(self, value):
        """Notifies all subscribed observers with the value."""

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                now = self.scheduler.now
                self.queue.append(dict(interval=now, value=value))
                self._trim(now)

                for observer in os:
                    observer.send(value)
        if os:
            for observer in os:
                observer.ensure_active()

    def throw(self, error):
        """Notifies all subscribed observers with the exception."""

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                self.error = error
                self.has_error = True
                now = self.scheduler.now
                self._trim(now)

                for observer in os:
                    observer.throw(error)
        if os:
            for observer in os:
                observer.ensure_active()

    def close(self):
        """Notifies all subscribed observers of the end of the sequence."""

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                now = self.scheduler.now
                self._trim(now)
                for observer in os:
                    observer.close()
        if os:
            for observer in os:
                observer.ensure_active()

    def dispose(self):
        """Releases all resources used by the current instance of the
        ReplaySubject class and unsubscribe all observers."""

        with self.lock:
            self.is_disposed = True
            self.observers = None
            self.queue = []
