from abc import abstractmethod
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, Union
from datetime import datetime, timedelta
from threading import Thread

from . import abc

T_out = TypeVar('T_out', covariant=True)
T_in = TypeVar('T_in', contravariant=True)
TState = TypeVar('TState')  # Can be anything
T1 = TypeVar('T1')
T2 = TypeVar('T2')


Action = Callable[[], None]

OnNext = Callable[[Any], None]
OnError = Callable[[Exception], None]
OnCompleted = Callable[[], None]

Mapper = Callable[[T1], T2]
MapperIndexed = Callable[[T1, int], T2]
Predicate = Callable[[T1], bool]
PredicateIndexed = Callable[[T1, int], bool]
Comparer = Callable[[T1, T2], bool]
SubComparer = Callable[[T1, T2], int]
Accumulator = Callable[[TState, T1], TState]
AbsoluteTime = Union[datetime, float]
RelativeTime = Union[timedelta, float]
AbsoluteOrRelativeTime = Union[datetime, timedelta, float]


class Disposable(abc.Disposable):
    """Disposable abstract base class."""

    __slots__ = ()

    @abstractmethod
    def dispose(self) -> None:
        """Dispose the object: stop whatever we're doing and release all of the
        resources we might be using.
        """

        raise NotImplementedError


class Scheduler(abc.Scheduler):
    """Scheduler abstract base class."""

    __slots__ = ()

    @property
    @abstractmethod
    def now(self) -> datetime:
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.

        Returns:
             The scheduler's current time, as a datetime instance.
        """

        return NotImplemented

    @abstractmethod
    def schedule(self,
                 action: 'ScheduledAction',
                 state: Optional[TState] = None
                 ) -> Disposable:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @abstractmethod
    def schedule_relative(self,
                          duetime: RelativeTime,
                          action: 'ScheduledAction',
                          state: Optional[TState] = None
                          ) -> Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @abstractmethod
    def schedule_absolute(self,
                          duetime: AbsoluteTime,
                          action: 'ScheduledAction',
                          state: Optional[TState] = None
                          ) -> Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_seconds(cls, value: AbsoluteOrRelativeTime) -> float:
        """Converts time value to seconds. This method handles both absolute
        (datetime) and relative (timedelta) values. If the argument is already
        a float, it is simply returned unchanged.

        Args:
            value: the time value to convert to seconds.

        Returns:
            The value converted to seconds.
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_datetime(cls, value: AbsoluteOrRelativeTime) -> datetime:
        """Converts time value to datetime. This method handles both absolute
        (float) and relative (timedelta) values. If the argument is already
        a datetime, it is simply returned unchanged.

        Args:
            value: the time value to convert to datetime.

        Returns:
            The value converted to datetime.
        """

        return NotImplemented

    @classmethod
    @abstractmethod
    def to_timedelta(cls, value: AbsoluteOrRelativeTime) -> timedelta:
        """Converts time value to timedelta. This method handles both absolute
        (datetime) and relative (float) values. If the argument is already
        a timedelta, it is simply returned unchanged. If the argument is an
        absolute time, the result value will be the timedelta since the epoch,
        January 1st, 1970, 00:00:00.

        Args:
            value: the time value to convert to timedelta.

        Returns:
            The value converted to timedelta.
        """

        return NotImplemented


class PeriodicScheduler(abc.PeriodicScheduler):
    """PeriodicScheduler abstract base class."""

    __slots__ = ()

    @abstractmethod
    def schedule_periodic(self,
                          period: RelativeTime,
                          action: 'ScheduledPeriodicAction',
                          state: Optional[TState] = None
                          ) -> Disposable:
        """Schedules a periodic piece of work.

        Args:
            period: Period in seconds or timedelta for running the
                work periodically.
            action: Action to be executed.
            state: [Optional] Initial state passed to the action upon
                the first iteration.

        Returns:
            The disposable object used to cancel the scheduled
            recurring action (best effort).
        """

        return NotImplemented


ScheduledAction = Callable[[Scheduler, Optional[TState]], Optional[Disposable]]
ScheduledPeriodicAction = Callable[[Optional[TState]], Optional[TState]]
ScheduledSingleOrPeriodicAction = Union[ScheduledAction, ScheduledPeriodicAction]


Startable = Union[abc.Startable, Thread]
StartableTarget = Callable[..., None]
StartableFactory = Callable[[StartableTarget], Startable]


class Observer(Generic[T_in], abc.Observer):
    """Observer abstract base class

    An Observer is the entity that receives all emissions of a subscribed
    Observable.
    """

    __slots__ = ()

    @abstractmethod
    def on_next(self, value: T_in) -> None:
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


class Observable(Generic[T_out], abc.Observable):
    """Observable abstract base class.

    Represents a push-style collection."""

    __slots__ = ()

    @abstractmethod
    def subscribe(self,
                  observer: Observer[T_out] = None,
                  *,
                  scheduler: Scheduler = None
                  ) -> Disposable:
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


class Subject(Generic[T_in, T_out], abc.Subject):
    """Subject abstract base class.

    Represents an object that is both an observable sequence as well
    as an observer.
    """

    __slots__ = ()

    @abstractmethod
    def subscribe(self,
                  observer: Observer[T_out] = None,
                  *,
                  scheduler: Scheduler = None
                  ) -> Disposable:
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
    def on_next(self, value: T_in) -> None:
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


Subscription = Callable[[Observer, Optional[Scheduler]], Disposable]
