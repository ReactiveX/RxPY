from abc import ABC, abstractmethod


class Observer(ABC):
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
