from abc import ABCMeta, abstractmethod


class Observable(metaclass=ABCMeta):
    @abstractmethod
    def subscribe(self, observer=None, scheduler=None):
        raise NotImplementedError
