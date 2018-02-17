from abc import abstractmethod

from .observable import Observable
from .observer import Observer


class Subject(Observer, Observable):
    """Subject abstract base class. Untyped."""
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

    @abstractmethod
    def subscribe(self, observer=None, scheduler=None):
        raise NotImplementedError