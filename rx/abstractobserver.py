class AbstractObserver(object):
    """Abstract Observer"""

    def __init__(self):
        self.is_stopped = False

    def next(self, value):
        raise NotImplementedError

    def error(self, error):
        raise NotImplementedError

    def completed(self):
        raise NotImplementedError

    def on_next(self, value):
        """Notifies the observer of a new element in the sequence.

        Keyword arguments:
        value -- Next element in the sequence.
        """
        if not self.is_stopped:
            self.next(value)

    def on_error(self, error):
        """Notifies the observer that an exception has occurred.

        Keyword arguments:
        error -- The error that has occurred.
        """
        if not self.is_stopped:
            self.is_stopped = True
            self.error(error)

    def on_completed(self):
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            self.is_stopped = True
            self.completed()

    def dispose(self):
        """Disposes the observer, causing it to transition to the stopped
        state."""

        self.is_stopped = True

    def fail(self, exn):
        if not self.is_stopped:
            self.is_stopped = True
            self.error(exn)
            return True

        return False