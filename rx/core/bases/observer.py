from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):
    @abstractmethod
    def on_next(self, value):
        raise NotImplementedError

    @abstractmethod
    def on_error(self, error):
        raise NotImplementedError

    @abstractmethod
    def on_completed(self):
        raise NotImplementedError
