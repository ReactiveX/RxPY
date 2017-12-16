from abc import ABC, abstractmethod


class Disposable(ABC):
    """Abstract disposable class"""

    @abstractmethod
    def dispose(self):
        raise NotImplementedError

    def __enter__(self):
        """Context management protocol."""
        pass

    def __exit__(self, type, value, traceback):
        """Context management protocol."""
        self.dispose()
