from abc import abstractmethod
from .observable import Observable, AsyncObservable


class Observer(Observable):
    """A synchronous observable."""

    __slots__ = ()

    @abstractmethod
    def send(self, value):
        return NotImplemented

    @abstractmethod
    def throw(self, error):
        return NotImplemented

    @abstractmethod
    def close(self):
        return NotImplemented

    def __subscribe__(self, observer):
        return self


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

    async def __asubscribe__(self, observer):
        return self
