from abc import abstractmethod
from rx.concurrency import immediate_scheduler

from . import Observer, AnonymousObserver
from .anonymousobservable import AnonymousObservable


class Notification:
    """Represents a notification to an observer."""

    def __init__(self):
        """Default constructor used by derived types."""
        self.has_value = False
        self.value = None
        self.kind = ''

    def accept(self, send, throw=None, close=None):
        """Invokes the delegate corresponding to the notification or an
        observer and returns the produced result.

        1 - notification.accept(observer)
        2 - notification.accept(send, throw, close)

        Keyword arguments:
        send -- Delegate to invoke for an OnNext notification.
        throw -- [Optional] Delegate to invoke for an OnError
            notification.
        close -- [Optional] Delegate to invoke for an OnCompleted
            notification.

        Returns result produced by the observation."""

        if isinstance(send, Observer):
            return self._accept_observer(send)
        else:
            return self._accept(send, throw, close)

    @abstractmethod
    def _accept(self, send, throw, close):
        raise NotImplementedError

    @abstractmethod
    def _accept_observer(self, observer):
        raise NotImplementedError

    def to_observable(self, scheduler=None):
        """Returns an observable sequence with a single notification,
        using the specified scheduler, else the immediate scheduler.

        Keyword arguments:
        scheduler -- [Optional] Scheduler to send out the notification
            calls on.

        Returns an observable sequence that surfaces the behavior of the
        notification upon subscription.
        """

        scheduler = scheduler or immediate_scheduler

        def subscribe(observer, scheduler=None):
            def action(scheduler, state):
                self._accept_observer(observer)
                if self.kind == 'N':
                    observer.close()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    def equals(self, other):
        """Indicates whether this instance and a specified object are
        equal."""

        other_string = '' if not other else str(other)
        return str(self) == other_string

    def __eq__(self, other):
        return self.equals(other)


class OnNext(Notification):
    """Represents an OnNext notification to an observer."""

    def __init__(self, value):
        """Constructs a notification of a new value."""

        super(OnNext, self).__init__()
        self.value = value
        self.has_value = True
        self.kind = 'N'

    def _accept(self, send, throw=None, close=None):
        return send(self.value)

    def _accept_observer(self, observer):
        return observer.send(self.value)

    def __str__(self):
        return "OnNext(%s)" % str(self.value)


class OnError(Notification):
    """Represents an OnError notification to an observer."""

    def __init__(self, exception):
        """Constructs a notification of an exception."""

        super(OnError, self).__init__()
        self.exception = exception
        self.kind = 'E'

    def _accept(self, send, throw, close):
        return throw(self.exception)

    def _accept_observer(self, observer):
        return observer.throw(self.exception)

    def __str__(self):
        return "OnError(%s)" % str(self.exception)


class OnCompleted(Notification):
    """Represents an OnCompleted notification to an observer."""

    def __init__(self):
        """Constructs a notification of the end of a sequence."""

        super(OnCompleted, self).__init__()
        self.kind = 'C'

    def _accept(self, send, throw, close):
        return close()

    def _accept_observer(self, observer):
        return observer.close()

    def __str__(self):
        return "OnCompleted()"


def from_notifier(handler):
    """Creates an observer from a notification callback.

    Keyword arguments:
    handler -- Action that handles a notification.

    Returns the observer object that invokes the specified handler using
    a notification corresponding to each message it receives.
    """

    def _send(value):
        return handler(OnNext(value))

    def _throw(error):
        return handler(OnError(error))

    def _close():
        return handler(OnCompleted())

    return AnonymousObserver(_send, _throw, _close)
