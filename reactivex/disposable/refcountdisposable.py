from threading import RLock
from typing import Optional

from reactivex.abc import DisposableBase

from .disposable import Disposable


class RefCountDisposable(DisposableBase):
    """Represents a disposable resource that only disposes its underlying
    disposable resource when all dependent disposable objects have been
    disposed."""

    class InnerDisposable(DisposableBase):
        def __init__(self, parent: "RefCountDisposable") -> None:
            self.parent: Optional[RefCountDisposable] = parent
            self.is_disposed = False
            self.lock = RLock()

        def dispose(self) -> None:
            with self.lock:
                parent = self.parent
                self.parent = None

            if parent is not None:
                parent.release()

    def __init__(self, disposable: DisposableBase) -> None:
        """Initializes a new instance of the RefCountDisposable class with the
        specified disposable."""

        self.underlying_disposable = disposable
        self.is_primary_disposed = False
        self.is_disposed = False
        self.lock = RLock()
        self.count = 0

        super().__init__()

    def dispose(self) -> None:
        """Disposes the underlying disposable only when all dependent
        disposable have been disposed."""

        if self.is_disposed:
            return

        underlying_disposable = None
        with self.lock:
            if not self.is_primary_disposed:
                self.is_primary_disposed = True
                if not self.count:
                    self.is_disposed = True
                    underlying_disposable = self.underlying_disposable

        if underlying_disposable is not None:
            underlying_disposable.dispose()

    def release(self) -> None:
        if self.is_disposed:
            return

        should_dispose = False
        with self.lock:
            self.count -= 1
            if not self.count and self.is_primary_disposed:
                self.is_disposed = True
                should_dispose = True

        if should_dispose:
            self.underlying_disposable.dispose()

    @property
    def disposable(self) -> DisposableBase:
        """Returns a dependent disposable that when disposed decreases the
        refcount on the underlying disposable."""

        with self.lock:
            if self.is_disposed:
                return Disposable()

            self.count += 1
            return self.InnerDisposable(self)
