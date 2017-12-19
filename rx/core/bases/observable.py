from abc import ABC, abstractmethod


class Observable(ABC):
    __slots__ = ()

    @abstractmethod
    def subscribe(self, observer=None, scheduler=None):
        raise NotImplementedError
