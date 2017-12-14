from abc import abstractmethod
from .asyncobservable import Observable, AsyncObservable


class AsyncObserver(AsyncObservable):
    """An asynchronous observable."""

    __slots__ = ()

    @abstractmethod
    async def asend(self, value):
        return NotImplemented

    @abstractmethod
    async def athrow(self, error):
        return NotImplemented

    @abstractmethod
    async def aclose(self):
        return NotImplemented

    async def asubscribe(self, observer):
        return self
