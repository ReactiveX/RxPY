from threading import RLock
from typing import Optional

from rx.core import typing
from rx.core.typing import Disposable


class SerialDisposable(Disposable):
    """Represents a disposable resource whose underlying disposable
    resource can be replaced by another disposable resource, causing
    automatic disposal of the previous underlying disposable resource.
    """

    def __init__(self) -> None:
        self.current: Optional[Disposable] = None
        self.is_disposed = False
        self.lock = RLock()

        super().__init__()

    def get_disposable(self) -> Optional[Disposable]:
        return self.current

    def set_disposable(self, value: typing.Disposable) -> None:
        """If the SerialDisposable has already been disposed, assignment
        to this property causes immediate disposal of the given
        disposable object. Assigning this property disposes the previous
        disposable object."""

        old: Optional[Disposable] = None

        with self.lock:
            should_dispose = self.is_disposed
            if not should_dispose:
                old = self.current
                self.current = value

        if old is not None:
            old.dispose()

        if should_dispose and value is not None:
            value.dispose()

    disposable = property(get_disposable, set_disposable)

    def dispose(self) -> None:
        """Disposes the underlying disposable as well as all future
        replacements."""

        old: Optional[Disposable] = None

        with self.lock:
            if not self.is_disposed:
                self.is_disposed = True
                old = self.current
                self.current = None

        if old is not None:
            old.dispose()
