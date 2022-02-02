from threading import RLock
from typing import Any, List

from rx.core.abc import DisposableBase


class CompositeDisposable(DisposableBase):
    """Represents a group of disposable resources that are disposed
    together"""

    def __init__(self, *args: Any):
        if args and isinstance(args[0], list):
            self.disposable: List[DisposableBase] = args[0]
        else:
            self.disposable = list(args)

        self.is_disposed = False
        self.lock = RLock()
        super(CompositeDisposable, self).__init__()

    def add(self, item: DisposableBase):
        """Adds a disposable to the CompositeDisposable or disposes the
        disposable if the CompositeDisposable is disposed

        Args:
            item: Disposable to add."""

        should_dispose = False
        with self.lock:
            if self.is_disposed:
                should_dispose = True
            else:
                self.disposable.append(item)

        if should_dispose:
            item.dispose()

    def remove(self, item: DisposableBase):
        """Removes and disposes the first occurrence of a disposable
        from the CompositeDisposable."""

        if self.is_disposed:
            return

        should_dispose = False
        with self.lock:
            if item in self.disposable:
                self.disposable.remove(item)
                should_dispose = True

        if should_dispose:
            item.dispose()

        return should_dispose

    def dispose(self) -> None:
        """Disposes all disposable in the group and removes them from
        the group."""

        if self.is_disposed:
            return

        with self.lock:
            self.is_disposed = True
            current_disposable = self.disposable
            self.disposable = []

        for disp in current_disposable:
            disp.dispose()

    def clear(self) -> None:
        """Removes and disposes all disposable from the
        CompositeDisposable, but does not dispose the
        CompositeDisposable."""

        with self.lock:
            current_disposable = self.disposable
            self.disposable = []

        for disposable in current_disposable:
            disposable.dispose()

    def contains(self, item: DisposableBase) -> bool:
        """Determines whether the CompositeDisposable contains a specific
        disposable.

        Args:
            item: Disposable to search for

        Returns:
            True if the disposable was found; otherwise, False"""

        return item in self.disposable

    def to_list(self):
        return self.disposable[:]

    def __len__(self):
        return len(self.disposable)

    @property
    def length(self):
        return len(self.disposable)
