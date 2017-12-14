from abc import ABCMeta, abstractmethod


class AsyncObservable(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    async def asubscribe(self, observer):
        raise NotImplementedError
