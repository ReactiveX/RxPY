from rx.internal import noop, default_error


class AbstractObserver(object):
    """Abstract base class for implementations of the Observer class. This base
    class enforces the grammar of observers where OnError and OnCompleted are
    terminal messages.
    """

    def __init__(self, on_next=None, on_error=None, on_completed=None):
        self.is_stopped = False

        # on_next now uses fast path and will be noop'ed when stopped
        if not hasattr(self, "on_next"):
            self.on_next = on_next or noop

        self._error = on_error or default_error
        self._completed = on_completed or noop

    def on_error(self, error):
        """Notifies the observer that an exception has occurred.

        Keyword arguments:
        error -- The error that has occurred."""

        if not self.is_stopped:
            AbstractObserver.dispose(self)
            self._error(error)

    def on_completed(self):
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            AbstractObserver.dispose(self)
            self._completed()

    def dispose(self):
        """Disposes the observer, causing it to transition to the stopped
        state."""

        self.on_next = noop
        self.is_stopped = True

    def fail(self, exn):
        if not self.is_stopped:
            AbstractObserver.dispose(self)
            self._error(exn)
            return True

        return False
