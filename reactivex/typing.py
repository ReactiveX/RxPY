from threading import Thread
from typing import Callable, TypeVar, Union

from .abc.observable import Subscription
from .abc.observer import OnCompleted, OnError, OnNext
from .abc.periodicscheduler import (
    ScheduledPeriodicAction,
    ScheduledSingleOrPeriodicAction,
)
from .abc.scheduler import (
    AbsoluteOrRelativeTime,
    AbsoluteTime,
    RelativeTime,
    ScheduledAction,
)
from .abc.startable import StartableBase

_TState = TypeVar("_TState")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

Action = Callable[[], None]

Mapper = Callable[[_T1], _T2]
MapperIndexed = Callable[[_T1, int], _T2]
Predicate = Callable[[_T1], bool]
PredicateIndexed = Callable[[_T1, int], bool]
Comparer = Callable[[_T1, _T1], bool]
SubComparer = Callable[[_T1, _T1], int]
Accumulator = Callable[[_TState, _T1], _TState]


Startable = Union[StartableBase, Thread]
StartableTarget = Callable[..., None]
StartableFactory = Callable[[StartableTarget], Startable]

__all__ = [
    "Accumulator",
    "AbsoluteTime",
    "AbsoluteOrRelativeTime",
    "Comparer",
    "Mapper",
    "MapperIndexed",
    "OnNext",
    "OnError",
    "OnCompleted",
    "Predicate",
    "PredicateIndexed",
    "RelativeTime",
    "SubComparer",
    "ScheduledPeriodicAction",
    "ScheduledSingleOrPeriodicAction",
    "ScheduledAction",
    "Startable",
    "StartableTarget",
    "Subscription",
]
