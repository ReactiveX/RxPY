from abc import abstractmethod
from typing import Generic, TypeVar, Callable, Any
from datetime import datetime, timedelta

from . import abc

T_out = TypeVar('T_out', covariant=True)
T_in = TypeVar('T_in', contravariant=True)

Action = Callable[[], None]
ScheduledAction = Callable[[abc.Scheduler, Any], None]

OnNext = Callable[[Any], None]                   # pylint: disable=C0103
OnError = Callable[[Exception], None]            # pylint: disable=C0103
OnCompleted = Callable[[], None]                 # pylint: disable=C0103

Mapper = Callable[[Any], Any]
MapperIndexed = Callable[[Any, int], Any]        # pylint: disable=C0103
Predicate = Callable[[Any], bool]                # pylint: disable=C0103
PredicateIndexed = Callable[[Any, int], bool]    # pylint: disable=C0103
Accumulator = Callable[[Any, Any], Any]          # pylint: disable=C0103
Dispose = Callable[[], None]                     # pylint: disable=C0103


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
    def schedule_relative(self, duetime: timedelta, action: ScheduledAction, state=None):
        return NotImplemented

    @abstractmethod
    def schedule_absolute(self, duetime, action: ScheduledAction, state=None):
        return NotImplemented


class Observer(Generic[T_in], abc.Observer):
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
