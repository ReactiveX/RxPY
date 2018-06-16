from abc import abstractmethod
from .asyncobservable import AsyncObservable


class AsyncObserver(AsyncObservable):
    """An asynchronous observable."""

    __slots__ = ()

    @abstractmethod
    async def on_next_async(self, value):
        return NotImplemented

    @abstractmethod
    async def on_error_async(self, error):
        return NotImplemented

    @abstractmethod
    async def on_completed_async(self):
        return NotImplemented

    async def subscribe_async(self, observer):
        return self
