from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):
    @abstractmethod
    def send(self, value):
        raise NotImplementedError

    @abstractmethod
    def throw(self, error):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
