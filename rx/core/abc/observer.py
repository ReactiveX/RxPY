from abc import ABC, abstractmethod


class Observer(ABC):
    """Observer abstract base class. Untyped."""

    __slots__ = ()

    @abstractmethod
    def on_next(self, value):
        raise NotImplementedError

    @abstractmethod
    def on_error(self, error):
        raise NotImplementedError

    @abstractmethod
    def on_completed(self):
        raise NotImplementedError
