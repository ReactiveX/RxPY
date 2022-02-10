from threading import RLock

from rx.core.abc import DisposableBase


class BooleanDisposable(DisposableBase):
    """Represents a Disposable that can be checked for status."""

    def __init__(self):
        """Initializes a new instance of the BooleanDisposable class."""

        self.is_disposed = False
        self.lock = RLock()

        super().__init__()

    def dispose(self) -> None:
        """Sets the status to disposed"""

        self.is_disposed = True
