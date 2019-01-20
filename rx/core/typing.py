from abc import abstractmethod
from typing import Generic, TypeVar, Callable, Any, Union
from datetime import datetime, timedelta

from . import abc

T_out = TypeVar('T_out', covariant=True)
T_in = TypeVar('T_in', contravariant=True)

Action = Callable[[], None]
ScheduledAction = Callable[[abc.Scheduler, Any], None]

OnNext = Callable[[Any], None]
OnError = Callable[[Exception], None]
OnCompleted = Callable[[], None]

Mapper = Callable[[Any], Any]
MapperIndexed = Callable[[Any, int], Any]
Predicate = Callable[[Any], bool]
PredicateIndexed = Callable[[Any, int], bool]
Accumulator = Callable[[Any, Any], Any]
AbsoluteTime = Union[datetime, float]
RelativeTime = Union[timedelta, float]
AbsoluteOrRelativeTime = Union[datetime, timedelta, float]


class Disposable(abc.Disposable):
    """Abstract disposable class"""

    __slots__ = ()

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError


class Scheduler(abc.Scheduler):
    __slots__ = ()

    @property
    @abstractmethod
    def now(self) -> datetime:
        return NotImplemented

    @abstractmethod
    def schedule(self, action: ScheduledAction, state: Any = None) -> Disposable:
        return NotImplemented

    @abstractmethod
    def schedule_relative(self, duetime: RelativeTime, action: ScheduledAction, state: Any = None) -> Disposable:
        return NotImplemented

    @abstractmethod
    def schedule_absolute(self, duetime: AbsoluteTime, action: ScheduledAction, state: Any = None) -> Disposable:
        return NotImplemented


class Observer(Generic[T_in], abc.Observer):
    """ Observer abstract base class

    An Observer is the entity that receives all emissions of a subscribed
    Observable.
    """
    __slots__ = ()

    @abstractmethod
    def on_next(self, value: T_in) -> None:
        """Notify the observer of a new element in the sequence.

        Args:
            value: The received element.
        """
        raise NotImplementedError

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """Notify the observer that an exception has occurred.

        Args:
            error: The error that has occurred.
        """
        raise NotImplementedError

    @abstractmethod
    def on_completed(self) -> None:
        """Notifies the observer of the end of the sequence."""
        raise NotImplementedError


class Observable(Generic[T_out], abc.Observable):
    __slots__ = ()

    @abstractmethod
    def subscribe(self, observer: Observer[T_out] = None, scheduler: Scheduler = None) -> Disposable:
        raise NotImplementedError


class Subject(Generic[T_in, T_out], abc.Subject):
    __slots__ = ()

    @abstractmethod
    def on_next(self, value: T_in) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_completed(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, observer: Observer[T_out] = None, scheduler: Scheduler = None) -> Disposable:
        raise NotImplementedError
