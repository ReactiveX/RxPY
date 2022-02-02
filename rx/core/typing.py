from threading import Thread
from typing import TYPE_CHECKING, Any, Callable, TypeVar, Union

from .abc.observable import Subscription
from .abc.observer import OnCompleted, OnError, OnNext
from .abc.periodicscheduler import (ScheduledPeriodicAction,
                                    ScheduledSingleOrPeriodicAction)
from .abc.scheduler import (AbsoluteOrRelativeTime, AbsoluteTime, RelativeTime,
                            ScheduledAction)
from .abc.startable import StartableBase

if TYPE_CHECKING:
    # Futures cannot take generic argument before Python 3.9
    class Future:
        """Mock future for type testing."""

        result: Any = None
        add_done_callback: Any = None
        cancel: Any = None

else:
    from asyncio.futures import Future

_TState = TypeVar("_TState")  # Can be anything
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

Action = Callable[[], None]

Mapper = Callable[[_T1], _T2]
MapperIndexed = Callable[[_T1, int], _T2]
Predicate = Callable[[_T1], bool]
PredicateIndexed = Callable[[_T1, int], bool]
Comparer = Callable[[_T1, _T2], bool]
SubComparer = Callable[[_T1, _T2], int]
Accumulator = Callable[[_TState, _T1], _TState]


Startable = Union[StartableBase, Thread]
StartableTarget = Callable[..., None]
StartableFactory = Callable[[StartableTarget], Startable]

__all__ = [
    "Accumulator",
    "AbsoluteTime",
    "AbsoluteOrRelativeTime",
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
    "Future",
]
