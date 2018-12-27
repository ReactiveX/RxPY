from abc import ABC, abstractmethod


class Disposable(ABC):
    """Disposable abstract base class. Untyped."""

    @abstractmethod
    def dispose(self):
        raise NotImplementedError

    def __enter__(self):
        """Context management protocol."""

    def __exit__(self, typ, value, traceback):
        """Context management protocol."""
        self.dispose()
