from rx import config
from rx.core import Observer, ObservableBase, Disposable
from rx.internal import DisposedException

from .innersubscription import InnerSubscription


class BehaviorSubject(ObservableBase, Observer):
    """Represents a value that changes over time. Observers can
    subscribe to the subject to receive the last (or initial) value and
    all subsequent notifications.
    """

    def __init__(self, value):
        """Initializes a new instance of the BehaviorSubject class which
        creates a subject that caches its last value and starts with the
        specified value.

        Keyword parameters:
        :param T value: Initial value sent to observers when no other
            value has been received by the subject yet.
        """

        super(BehaviorSubject, self).__init__()

        self.value = value
        self.observers = []
        self.is_disposed = False
        self.is_stopped = False
        self.exception = None

        self.lock = config["concurrency"].RLock()

    def check_disposed(self):
        if self.is_disposed:
            raise DisposedException()

    def _subscribe_core(self, observer, scheduler=None):
        ex = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.observers.append(observer)
                observer.send(self.value)
                return InnerSubscription(self, observer)
            ex = self.exception

        if ex:
            observer.throw(ex)
        else:
            observer.close()

        return Disposable.empty()

    def close(self):
        """Notifies all subscribed observers of the end of the sequence."""

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True

        if os:
            for o in os:
                o.close()

    def throw(self, error):
        """Notifie all subscribed observers with the exception."""
        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                self.exception = error

        if os:
            for o in os:
                o.throw(error)

    def send(self, value):
        """Notifie all subscribed observers with the value."""
        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.value = value
        if os:
            for o in os:
                o.send(value)

    def dispose(self):
        """Release all resources.

        Releases all resources used by the current instance of the
        ReplaySubject class and unsubscribe all observers.
        """
        with self.lock:
            self.is_disposed = True
            self.observers = None
            self.value = None
            self.exception = None
