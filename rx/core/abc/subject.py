from abc import abstractmethod

from .observable import Observable
from .observer import Observer


class Subject(Observer, Observable):
    """Subject abstract base class. Untyped."""
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

    @abstractmethod
    def subscribe(self, observer=None, *, scheduler=None):
        raise NotImplementedError
