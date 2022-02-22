from abc import abstractmethod
from typing import Optional, TypeVar, Union

from .disposable import DisposableBase
from .observable import ObservableBase
from .observer import ObserverBase, OnCompleted, OnError, OnNext
from .scheduler import SchedulerBase

_T = TypeVar("_T")


class SubjectBase(ObserverBase[_T], ObservableBase[_T]):
    """Subject abstract base class.

    Represents an object that is both an observable sequence as well
    as an observer.
    """

    __slots__ = ()

    @abstractmethod
    def subscribe(
        self,
        on_next: Optional[Union[OnNext[_T], ObserverBase[_T]]] = None,
        on_error: Optional[OnError] = None,
        on_completed: Optional[OnCompleted] = None,
        *,
        scheduler: Optional[SchedulerBase] = None,
    ) -> DisposableBase:
        """Subscribe an observer to the observable sequence.

        Args:
            observer: [Optional] The object that is to receive
                notifications.
            scheduler: [Optional] The default scheduler to use for this
                subscription.

        Returns:
            Disposable object representing an observer's subscription
            to the observable sequence.
        """

        raise NotImplementedError

    @abstractmethod
    def on_next(self, value: _T) -> None:
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


__all__ = ["SubjectBase"]
