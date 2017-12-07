from abc import abstractmethod

from rx.internal import noop
from . import Observer, Disposable


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
            ObserverBase.dispose(self)
            self._throw_core(error)

    @abstractmethod
    def _throw_core(self, error):
        return NotImplemented

    def close(self):
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            ObserverBase.dispose(self)
            self._close_core()

    @abstractmethod
    def _close_core(self):
        return NotImplemented

    def dispose(self):
        """Disposes the observer, causing it to transition to the stopped
        state."""

        self.send = noop
        self.is_stopped = True

    def fail(self, exn):
        if not self.is_stopped:
            ObserverBase.dispose(self)
            self._throw_core(exn)
            return True

        return False
