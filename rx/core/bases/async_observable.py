from abc import ABCMeta, abstractmethod


class Observable(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    def __subscribe__(self, observer):
        return NotImplemented


class AsyncObservable(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    async def __asubscribe__(self, observer):
        return NotImplemented
