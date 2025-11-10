from collections.abc import Callable
from threading import Thread
from typing import TypeAlias, TypeVar

from typing_extensions import TypeAliasType

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

# Non-generic type aliases
Action: TypeAlias = Callable[[], None]
Startable: TypeAlias = StartableBase | Thread
StartableTarget: TypeAlias = Callable[..., None]
StartableFactory: TypeAlias = Callable[[StartableTarget], Startable]

# Generic type aliases
Mapper = TypeAliasType("Mapper", Callable[[_T1], _T2], type_params=(_T1, _T2))
MapperIndexed = TypeAliasType(
    "MapperIndexed", Callable[[_T1, int], _T2], type_params=(_T1, _T2)
)
Predicate = TypeAliasType("Predicate", Callable[[_T1], bool], type_params=(_T1,))
PredicateIndexed = TypeAliasType(
    "PredicateIndexed", Callable[[_T1, int], bool], type_params=(_T1,)
)
Comparer = TypeAliasType("Comparer", Callable[[_T1, _T1], bool], type_params=(_T1,))
SubComparer = TypeAliasType(
    "SubComparer", Callable[[_T1, _T1], int], type_params=(_T1,)
)
Accumulator = TypeAliasType(
    "Accumulator", Callable[[_TState, _T1], _TState], type_params=(_TState, _T1)
)

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
