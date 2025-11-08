from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

from .disposable import DisposableBase
from .observer import ObserverBase, OnCompleted, OnError, OnNext
from .scheduler import SchedulerBase

_T_out = TypeVar("_T_out", covariant=True)


class ObservableBase(Generic[_T_out], ABC):
    """Observable abstract base class.

    Represents a push-style collection."""

    __slots__ = ()

    @abstractmethod
    def subscribe(
        self,
        on_next: OnNext[_T_out] | ObserverBase[_T_out] | None = None,
        on_error: OnError | None = None,
        on_completed: OnCompleted | None = None,
        *,
        scheduler: SchedulerBase | None = None,
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


Subscription = Callable[[ObserverBase[_T_out], SchedulerBase | None], DisposableBase]

__all__ = ["ObservableBase", "Subscription"]
