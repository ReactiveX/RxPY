from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type


class DisposableBase(ABC):
    """Disposable abstract base class."""

    __slots__ = ()

    @abstractmethod
    def dispose(self) -> None:
        """Dispose the object: stop whatever we're doing and release all of the
        resources we might be using.
        """
        raise NotImplementedError

    def __enter__(self) -> DisposableBase:
        """Context management protocol."""
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> None:
        """Context management protocol."""
        self.dispose()


__all__ = ["DisposableBase"]
