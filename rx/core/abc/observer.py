from abc import ABC, abstractmethod


class Observer(ABC):
    """Observer abstract base class. Untyped."""

    __slots__ = ()

    @abstractmethod
    def send(self, value):
        raise NotImplementedError

    @abstractmethod
    def throw(self, error):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
