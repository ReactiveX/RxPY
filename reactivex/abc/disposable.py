from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType


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
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ) -> None:
        """Context management protocol."""
        self.dispose()


__all__ = ["DisposableBase"]
