import sys
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Deque, NamedTuple, Optional, TypeVar, cast

from reactivex.observer.scheduledobserver import ScheduledObserver
from reactivex.scheduler import CurrentThreadScheduler

from .. import abc, typing
from ..observer import Observer
from .subject import Subject

_T = TypeVar("_T")


class RemovableDisposable(abc.DisposableBase):
    def __init__(self, subject: Subject[_T], observer: Observer[_T]):
        self.subject = subject
        self.observer = observer

    def dispose(self) -> None:
        self.observer.dispose()
        if not self.subject.is_disposed and self.observer in self.subject.observers:
            self.subject.observers.remove(self.observer)


class QueueItem(NamedTuple):
    interval: datetime
    value: Any


class ReplaySubject(Subject[_T]):
    """Represents an object that is both an observable sequence as well
    as an observer. Each notification is broadcasted to all subscribed
    and future observers, subject to buffer trimming policies.
    """

    def __init__(
        self,
        buffer_size: Optional[int] = None,
        window: Optional[typing.RelativeTime] = None,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> None:
        """Initializes a new instance of the ReplaySubject class with
        the specified buffer size, window and scheduler.

        Args:
            buffer_size: [Optional] Maximum element count of the replay
                buffer.
            window [Optional]: Maximum time length of the replay buffer.
            scheduler: [Optional] Scheduler the observers are invoked on.
        """

        super().__init__()
        self.buffer_size = sys.maxsize if buffer_size is None else buffer_size
        self.scheduler = scheduler or CurrentThreadScheduler.singleton()
        self.window = (
            timedelta.max if window is None else self.scheduler.to_timedelta(window)
        )
        self.queue: Deque[QueueItem] = deque()

    def _subscribe_core(
        self,
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        so = ScheduledObserver(self.scheduler, observer)
        subscription = RemovableDisposable(self, so)

        with self.lock:
            self.check_disposed()
            self._trim(self.scheduler.now)
            self.observers.append(so)

            for item in self.queue:
                so.on_next(item.value)

            if self.exception is not None:
                so.on_error(self.exception)
            elif self.is_stopped:
                so.on_completed()

        so.ensure_active()
        return subscription

    def _trim(self, now: datetime) -> None:
        while len(self.queue) > self.buffer_size:
            self.queue.popleft()

        while self.queue and (now - self.queue[0].interval) > self.window:
            self.queue.popleft()

    def _on_next_core(self, value: _T) -> None:
        """Notifies all subscribed observers with the value."""

        with self.lock:
            observers = self.observers.copy()
            now = self.scheduler.now
            self.queue.append(QueueItem(interval=now, value=value))
            self._trim(now)

        for observer in observers:
            observer.on_next(value)

        for observer in observers:
            cast(ScheduledObserver[_T], observer).ensure_active()

    def _on_error_core(self, error: Exception) -> None:
        """Notifies all subscribed observers with the exception."""

        with self.lock:
            observers = self.observers.copy()
            self.observers.clear()
            self.exception = error
            now = self.scheduler.now
            self._trim(now)

        for observer in observers:
            observer.on_error(error)
            cast(ScheduledObserver[_T], observer).ensure_active()

    def _on_completed_core(self) -> None:
        """Notifies all subscribed observers of the end of the sequence."""

        with self.lock:
            observers = self.observers.copy()
            self.observers.clear()
            now = self.scheduler.now
            self._trim(now)

        for observer in observers:
            observer.on_completed()
            cast(ScheduledObserver[_T], observer).ensure_active()

    def dispose(self) -> None:
        """Releases all resources used by the current instance of the
        ReplaySubject class and unsubscribe all observers."""

        with self.lock:
            self.queue.clear()
            super().dispose()
