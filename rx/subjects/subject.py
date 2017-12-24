from rx import config
from rx.core import Observer, ObservableBase, Disposable
from rx.internal import DisposedException

from .anonymoussubject import AnonymousSubject
from .innersubscription import InnerSubscription


class Subject(ObservableBase, Observer):
    """Represents an object that is both an observable sequence as well as an
    observer. Each notification is broadcasted to all subscribed observers.
    """

    def __init__(self):
        super(Subject, self).__init__()

        self.is_disposed = False
        self.is_stopped = False
        self.observers = []
        self.exception = None

        self.lock = config["concurrency"].RLock()

    def check_disposed(self):
        if self.is_disposed:
            raise DisposedException()

    def _subscribe_core(self, observer, scheduler=None):
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.observers.append(observer)
                return InnerSubscription(self, observer)

            if self.exception:
                observer.throw(self.exception)
                return Disposable.empty()

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
            for observer in os:
                observer.close()

    def throw(self, error):
        """Notifies all subscribed observers with the exception.

        Keyword arguments:
        error -- The exception to send to all subscribed observers.
        """

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                self.exception = error

        if os:
            for observer in os:
                observer.throw(error)

    def send(self, value):
        """Notifies all subscribed observers with the value.

        Keyword arguments:
        value -- The value to send to all subscribed observers.
        """

        os = None
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]

        if os:
            for observer in os:
                observer.send(value)

    def dispose(self):
        """Unsubscribe all observers and release resources."""
        print("dispose!")
        with self.lock:
            self.is_disposed = True
            self.observers = None

    @classmethod
    def create(cls, observer, observable):
        return AnonymousSubject(observer, observable)
