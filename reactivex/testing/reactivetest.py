import math
import types
from typing import Any, Generic, TypeVar, Union

from reactivex import typing
from reactivex.notification import OnCompleted, OnError, OnNext

from .recorded import Recorded
from .subscription import Subscription

_T = TypeVar("_T")


def is_prime(i: int) -> bool:
    """Tests if number is prime or not"""

    if i <= 1:
        return False

    _max = int(math.floor(math.sqrt(i)))
    for j in range(2, _max + 1):
        if not i % j:
            return False

    return True


# New predicate tests
class OnNextPredicate(Generic[_T]):
    def __init__(self, predicate: typing.Predicate[_T]) -> None:
        self.predicate = predicate

    def __eq__(self, other: Any) -> bool:
        if other == self:
            return True
        if other is None:
            return False
        if other.kind != "N":
            return False
        return self.predicate(other.value)


class OnErrorPredicate(Generic[_T]):
    def __init__(self, predicate: typing.Predicate[_T]):
        self.predicate = predicate

    def __eq__(self, other: Any) -> bool:
        if other == self:
            return True
        if other is None:
            return False
        if other.kind != "E":
            return False
        return self.predicate(other.exception)


class ReactiveTest:
    created = 100
    subscribed = 200
    disposed = 1000

    @staticmethod
    def on_next(ticks: int, value: _T) -> Recorded[_T]:
        if isinstance(value, types.FunctionType):
            return Recorded(ticks, OnNextPredicate(value))

        return Recorded(ticks, OnNext(value))

    @staticmethod
    def on_error(ticks: int, error: Union[Exception, str]) -> Recorded[Any]:
        if isinstance(error, types.FunctionType):
            return Recorded(ticks, OnErrorPredicate(error))

        return Recorded(ticks, OnError(error))

    @staticmethod
    def on_completed(ticks: int) -> Recorded[Any]:
        return Recorded(ticks, OnCompleted())

    @staticmethod
    def subscribe(start: int, end: int) -> Subscription:
        return Subscription(start, end)
