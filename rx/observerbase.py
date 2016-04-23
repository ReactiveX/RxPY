from rx.internal import noop
from rx.abc import Observer


class ObserverBase(Observer):
    """Base class for implementations of the Observer class. This base
    class enforces the grammar of observers where OnError and
    OnCompleted are terminal messages.
    """

    def __init__(self):
        self.is_stopped = False

    def on_next(self, value):
        """Notify the observer of a new element in the sequence."""
        if not self.is_stopped:
            self._next(value)

    def on_error(self, error):
        """Notifies the observer that an exception has occurred.

        Keyword arguments:
        error -- The error that has occurred."""

        if not self.is_stopped:
            ObserverBase.dispose(self)
            self._error(error)

    def on_completed(self):
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            ObserverBase.dispose(self)
            self._completed()

    def dispose(self):
        """Disposes the observer, causing it to transition to the stopped
        state."""

        self.on_next = noop
        self.is_stopped = True

    def fail(self, exn):
        if not self.is_stopped:
            ObserverBase.dispose(self)
            self._error(exn)
            return True

        return False
