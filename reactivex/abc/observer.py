from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

_T = TypeVar("_T")
_T_in = TypeVar("_T_in", contravariant=True)

OnNext = Callable[[_T], None]
OnError = Callable[[Exception], None]
OnCompleted = Callable[[], None]


class ObserverBase(Generic[_T_in], ABC):
    """Observer abstract base class

    An Observer is the entity that receives all emissions of a
    subscribed Observable.
    """

    __slots__ = ()

    @abstractmethod
    def on_next(self, value: _T_in) -> None:
        """Notifies the observer of a new element in the sequence.

        Args:
            value: The received element.
        """

        raise NotImplementedError

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """Notifies the observer that an exception has occurred.

        Args:
            error: The error that has occurred.
        """

        raise NotImplementedError

    @abstractmethod
    def on_completed(self) -> None:
        """Notifies the observer of the end of the sequence."""

        raise NotImplementedError


__all__ = ["ObserverBase", "OnNext", "OnError", "OnCompleted"]
