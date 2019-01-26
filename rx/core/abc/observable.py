from abc import ABC, abstractmethod


class Observable(ABC):
    """Observable abstract base class. Untyped."""

    __slots__ = ()

    @abstractmethod
    def subscribe(self, observer=None, *, scheduler=None):
        raise NotImplementedError
