from typing import Callable
from abc import abstractmethod

from .disposable import Disposable
from .typing import Observer


class ObserverBase(Observer, Disposable):
    """Base class for implementations of the Observer class. This base
    class enforces the grammar of observers where OnError and
    OnCompleted are terminal messages.
    """

    def __init__(self):
        self.is_stopped = False

    def send(self, value):
        """Notify the observer of a new element in the sequence."""
        if not self.is_stopped:
            self._send_core(value)

    @abstractmethod
    def _send_core(self, value):
        return NotImplemented

    def throw(self, error):
        """Notifies the observer that an exception has occurred.

        Keyword arguments:
        error -- The error that has occurred."""

        if not self.is_stopped:
            self.is_stopped = True
            self._throw_core(error)

    @abstractmethod
    def _throw_core(self, error):
        return NotImplemented

    def close(self):
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            self.is_stopped = True
            self._close_core()

    @abstractmethod
    def _close_core(self):
        return NotImplemented

    def dispose(self):
        """Disposes the observer, causing it to transition to the stopped
        state."""

        self.is_stopped = True

    def fail(self, exn):
        if not self.is_stopped:
            self.is_stopped = True
            self._throw_core(exn)
            return True

        return False

    def to_notifier(self) -> Callable:
        """Creates a notification callback from an observer.

        Returns the action that forwards its input notification to the
        underlying observer."""

        def func(notifier):
            return notifier.accept(self)
        return func

    def as_observer(self) -> 'ObserverBase':
        """Hides the identity of an observer.

        Returns an observer that hides the identity of the specified
        observer.
        """
        from .observerextensions import as_observer
        return as_observer(self)

    def checked(self) -> 'ObserverBase':
        """Checks access to the observer for grammar violations. This
        includes checking for multiple OnError or OnCompleted calls,
        as well as reentrancy in any of the observer methods. If a
        violation is detected, an Error is thrown from the offending
        observer method call.

        Returns an observer that checks callbacks invocations against
        the observer grammar and, if the checks pass, forwards those to
        the specified observer."""

        from .checkedobserver import CheckedObserver
        return CheckedObserver(self)
