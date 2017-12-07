from rx import config
from rx.core import Observer, Observable, Disposable
from rx.internal import DisposedException

from .innersubscription import InnerSubscription


class AsyncSubject(Observable, Observer):
    """Represents the result of an asynchronous operation. The last value
    before the close notification, or the error received through
    throw, is sent to all subscribed observers."""

    def __init__(self):
        """Creates a subject that can only receive one value and that value is
        cached for all future observations."""

        super(AsyncSubject, self).__init__()

        self.is_disposed = False
        self.is_stopped = False
        self.value = None
        self.has_value = False
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

            ex = self.exception
            hv = self.has_value
            v = self.value

        if ex:
            observer.throw(ex)
        elif hv:
            observer.send(v)
            observer.close()
        else:
            observer.close()

        return Disposable.empty()

    def close(self):
        value = None
        os = None
        hv = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []

                self.is_stopped = True
                value = self.value
                hv = self.has_value

        if os:
            if hv:
                for o in os:
                    o.send(value)
                    o.close()
            else:
                for o in os:
                    o.close()

    def throw(self, exception):
        os = None

        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                os = self.observers[:]
                self.observers = []
                self.is_stopped = True
                self.exception = exception

        if os:
            for o in os:
                o.throw(exception)

    def send(self, value):
        with self.lock:
            self.check_disposed()
            if not self.is_stopped:
                self.value = value
                self.has_value = True

    def dispose(self):
        with self.lock:
            self.is_disposed = True
            self.observers = None
            self.exception = None
            self.value = None

