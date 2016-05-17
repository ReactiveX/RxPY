from rx import Lock
from rx.core import Disposable


class BooleanDisposable(Disposable):
    """Represents a Disposable that can be checked for status."""

    def __init__(self, is_single=True):
        """Initializes a new instance of the BooleanDisposable class."""

        self.is_single = is_single
        self.is_disposed = False
        self.current = None
        self.lock = Lock()

        super(BooleanDisposable, self).__init__()

    def get_disposable(self):
        return self.current

    def set_disposable(self, value):
        if self.current and self.is_single:
            raise Exception('Disposable has already been assigned')

        should_dispose = self.is_disposed
        old = None

        with self.lock:
            if not should_dispose:
                old = self.current
                self.current = value

        if old:
            old.dispose()

        if should_dispose and value:
            value.dispose()

    disposable = property(get_disposable, set_disposable)

    def dispose(self):
        """Sets the status to disposed"""
        old = None

        with self.lock:
            if not self.is_disposed:
                self.is_disposed = True
                old = self.current
                self.current = None

        if old:
            old.dispose()
