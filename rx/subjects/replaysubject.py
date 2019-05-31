import sys
import threading
from typing import Any, Optional, List
from datetime import timedelta

from rx.core import Observable, typing
from rx.core.typing import Observer
from rx.internal import DisposedException
from rx.scheduler import current_thread_scheduler
from rx.core.observer.scheduledobserver import ScheduledObserver


class RemovableDisposable:
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer

    def dispose(self):
        self.observer.dispose()
        if not self.subject.is_disposed and self.observer in self.subject.observers:
            self.subject.observers.remove(self.observer)


class ReplaySubject(Observable, Observer):
    """Represents an object that is both an observable sequence as well
    as an observer. Each notification is broadcasted to all subscribed
    and future observers, subject to buffer trimming policies.
    """

    def __init__(self, buffer_size: int = None, window: typing.RelativeTime = None, scheduler: typing.Scheduler = None):
        """Initializes a new instance of the ReplaySubject class with
        the specified buffer size, window and scheduler.

        Args:
            buffer_size: [Optional] Maximum element count of the replay
                buffer.
            window [Optional]: Maximum time length of the replay buffer.
            scheduler: [Optional] Scheduler the observers are invoked on.
        """

        self.buffer_size = sys.maxsize if buffer_size is None else buffer_size
        self.scheduler = scheduler or current_thread_scheduler
        self.window = timedelta.max if window is None else self.scheduler.to_timedelta(window)
        self.queue: List[Any] = []
        self.observers: List[ScheduledObserver] = []
        self.is_stopped = False
        self.is_disposed = False
        self.has_error = False
        self.error: Optional[Exception] = None

        self.lock = threading.RLock()

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
                so.on_next(item['value'])

            if self.has_error:
                so.on_error(self.error)
            elif self.is_stopped:
                so.on_completed()

        so.ensure_active()
        return subscription

    def _trim(self, now):
        while len(self.queue) > self.buffer_size:
            self.queue.pop(0)

        while self.queue and (now - self.queue[0]['interval']) > self.window:
            self.queue.pop(0)

    def on_next(self, value: Any) -> None:
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
                    observer.on_next(value)
        if os:
            for observer in os:
                observer.ensure_active()

    def on_error(self, error: Exception) -> None:
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
                    observer.on_error(error)
        if os:
            for observer in os:
                observer.ensure_active()

    def on_completed(self) -> None:
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
                    observer.on_completed()
        if os:
            for observer in os:
                observer.ensure_active()

    def dispose(self) -> None:
        """Releases all resources used by the current instance of the
        ReplaySubject class and unsubscribe all observers."""

        with self.lock:
            self.is_disposed = True
            self.observers = []
            self.queue = []
