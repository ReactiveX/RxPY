from abc import ABC, abstractmethod


class Observable(ABC):
    """Observable abstract base class. Untyped."""

    __slots__ = ()

    @abstractmethod
    def subscribe(self, on_next=None, on_error=None, on_completed=None,
                  *, scheduler=None):
        raise NotImplementedError

    @abstractmethod
    def subscribe_observer(self, observer=None, *, scheduler=None):
        raise NotImplementedError
