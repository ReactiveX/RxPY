from abc import abstractmethod
from types import TracebackType
from typing import Optional, Protocol, Type, runtime_checkable


@runtime_checkable
class DisposableBase(Protocol):
    """Disposable abstract base class. Untyped."""

    __slots__ = ()

    @abstractmethod
    def dispose(self) -> None:
        """Dispose the object: stop whatever we're doing and release all of the
        resources we might be using.
        """
        raise NotImplementedError

    def __enter__(self):
        """Context management protocol."""

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ):
        """Context management protocol."""
        self.dispose()
