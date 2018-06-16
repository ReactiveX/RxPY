from abc import ABCMeta, abstractmethod


class AsyncObservable(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    async def subscribe_async(self, observer):
        raise NotImplementedError
