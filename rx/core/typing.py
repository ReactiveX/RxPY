from abc import abstractmethod
from typing import Generic, TypeVar, Callable, Any
from datetime import datetime, timedelta

from . import bases

T_out = TypeVar('T_out', covariant=True)
T_in = TypeVar('T_in', contravariant=True)

Action = Callable[[bases.Scheduler, Any], None]  # pylint: disable=C0103
Send = Callable[[Any], None]                     # pylint: disable=C0103
Throw = Callable[[Exception], None]              # pylint: disable=C0103
Close = Callable[[None], None]                   # pylint: disable=C0103


class Disposable(bases.Disposable):
    """Abstract disposable class"""

    __slots__ = ()

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError


class Scheduler(bases.Scheduler):
    __slots__ = ()

    @property
    @abstractmethod
    def now(self) -> datetime:
        return NotImplemented

    @abstractmethod
    def schedule(self, action: Action, state: Any = None) -> Disposable:
        return NotImplemented

    @abstractmethod
    def schedule_relative(self, duetime: timedelta, action: Action, state=None):
        return NotImplemented

    @abstractmethod
    def schedule_absolute(self, duetime, action: Action, state=None):
        return NotImplemented

class Observer(Generic[T_in], bases.Observer):
    __slots__ = ()

    @abstractmethod
    def send(self, value: T_in) -> None:
        raise NotImplementedError

    @abstractmethod
    def throw(self, error: Exception) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class Observable(Generic[T_out], bases.Observable):
    __slots__ = ()

    @abstractmethod
    def subscribe(self, observer: Observer[T_out] = None, scheduler: Scheduler = None) -> Disposable:
        raise NotImplementedError
