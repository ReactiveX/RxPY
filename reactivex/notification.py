from abc import abstractmethod
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from reactivex import abc, typing
from reactivex.scheduler import ImmediateScheduler

from .observable import Observable
from .observer import Observer

_T = TypeVar("_T")


class Notification(Generic[_T]):
    """Represents a notification to an observer."""

    def __init__(self) -> None:
        """Default constructor used by derived types."""
        self.has_value = False
        self.value: Optional[_T] = None
        self.kind: str = ""

    def accept(
        self,
        on_next: Union[typing.OnNext[_T], abc.ObserverBase[_T]],
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
    ) -> None:
        """Invokes the delegate corresponding to the notification or an
        observer and returns the produced result.

        Examples:
            >>> notification.accept(observer)
            >>> notification.accept(on_next, on_error, on_completed)

        Args:
            on_next: Delegate to invoke for an OnNext notification.
            on_error: [Optional] Delegate to invoke for an OnError
                notification.
            on_completed: [Optional] Delegate to invoke for an
                OnCompleted notification.

        Returns:
            Result produced by the observation."""

        if isinstance(on_next, abc.ObserverBase):
            return self._accept_observer(on_next)

        return self._accept(on_next, on_error, on_completed)

    @abstractmethod
    def _accept(
        self,
        on_next: typing.OnNext[_T],
        on_error: Optional[typing.OnError],
        on_completed: Optional[typing.OnCompleted],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def _accept_observer(self, observer: abc.ObserverBase[_T]) -> None:
        raise NotImplementedError

    def to_observable(
        self, scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.ObservableBase[_T]:
        """Returns an observable sequence with a single notification,
        using the specified scheduler, else the immediate scheduler.

        Args:
            scheduler: [Optional] Scheduler to send out the
                notification calls on.

        Returns:
            An observable sequence that surfaces the behavior of the
            notification upon subscription.
        """

        _scheduler = scheduler or ImmediateScheduler.singleton()

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            def action(scheduler: abc.SchedulerBase, state: Any) -> None:
                self._accept_observer(observer)
                if self.kind == "N":
                    observer.on_completed()

            __scheduler = scheduler or _scheduler
            return __scheduler.schedule(action)

        return Observable(subscribe)

    def equals(self, other: "Notification[_T]") -> bool:
        """Indicates whether this instance and a specified object are
        equal."""

        other_string = "" if not other else str(other)
        return str(self) == other_string

    def __eq__(self, other: Any) -> bool:
        return self.equals(other)


class OnNext(Notification[_T]):
    """Represents an OnNext notification to an observer."""

    def __init__(self, value: _T) -> None:
        """Constructs a notification of a new value."""

        super(OnNext, self).__init__()
        self.value: _T = value
        self.has_value: bool = True
        self.kind: str = "N"

    def _accept(
        self,
        on_next: typing.OnNext[_T],
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
    ) -> None:
        return on_next(self.value)

    def _accept_observer(self, observer: abc.ObserverBase[_T]) -> None:
        return observer.on_next(self.value)

    def __str__(self) -> str:
        val: Any = self.value
        if isinstance(val, int):
            val = float(val)
        return "OnNext(%s)" % str(val)


class OnError(Notification[_T]):
    """Represents an OnError notification to an observer."""

    def __init__(self, error: Union[Exception, str]) -> None:
        """Constructs a notification of an exception."""

        super(OnError, self).__init__()
        self.exception: Exception = (
            error if isinstance(error, Exception) else Exception(error)
        )
        self.kind = "E"

    def _accept(
        self,
        on_next: typing.OnNext[_T],
        on_error: Optional[typing.OnError],
        on_completed: Optional[typing.OnCompleted],
    ) -> None:
        return on_error(self.exception) if on_error else None

    def _accept_observer(self, observer: abc.ObserverBase[_T]) -> None:
        return observer.on_error(self.exception)

    def __str__(self) -> str:
        return "OnError(%s)" % str(self.exception)


class OnCompleted(Notification[_T]):
    """Represents an OnCompleted notification to an observer."""

    def __init__(self) -> None:
        """Constructs a notification of the end of a sequence."""

        super(OnCompleted, self).__init__()
        self.kind = "C"

    def _accept(
        self,
        on_next: typing.OnNext[_T],
        on_error: Optional[typing.OnError],
        on_completed: Optional[typing.OnCompleted],
    ) -> None:
        return on_completed() if on_completed else None

    def _accept_observer(self, observer: abc.ObserverBase[_T]) -> None:
        return observer.on_completed()

    def __str__(self) -> str:
        return "OnCompleted()"


def from_notifier(handler: Callable[[Notification[_T]], None]) -> Observer[_T]:
    """Creates an observer from a notification callback.

    Args:
        handler: Action that handles a notification.

    Returns:
        The observer object that invokes the specified handler using
        a notification corresponding to each message it receives.
    """

    def _on_next(value: _T) -> None:
        return handler(OnNext(value))

    def _on_error(error: Exception) -> None:
        return handler(OnError(error))

    def _on_completed() -> None:
        return handler(OnCompleted())

    return Observer(_on_next, _on_error, _on_completed)
