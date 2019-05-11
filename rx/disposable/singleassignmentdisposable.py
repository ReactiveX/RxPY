from threading import RLock
from rx.core.typing import Disposable


class SingleAssignmentDisposable(Disposable):
    """Single assignment disposable.

    Represents a disposable resource which only allows a single
    assignment of its underlying disposable resource. If an underlying
    disposable resource has already been set, future attempts to set the
    underlying disposable resource will throw an Error."""

    def __init__(self) -> None:
        """Initializes a new instance of the SingleAssignmentDisposable
        class.
        """
        self.is_disposed = False
        self.current = None
        self.lock = RLock()

        super().__init__()

    def get_disposable(self):
        return self.current

    def set_disposable(self, value):
        if self.current:
            raise Exception('Disposable has already been assigned')

        old = None

        with self.lock:
            should_dispose = self.is_disposed
            if not should_dispose:
                old = self.current
                self.current = value

        if old:
            old.dispose()

        if should_dispose and value:
            value.dispose()

    disposable = property(get_disposable, set_disposable)

    def dispose(self) -> None:
        """Sets the status to disposed"""
        old = None

        with self.lock:
            if not self.is_disposed:
                self.is_disposed = True
                old = self.current
                self.current = None

        if old is not None:
            old.dispose()
