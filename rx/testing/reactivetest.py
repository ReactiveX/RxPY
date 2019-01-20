from typing import Any

import math
import types

from rx.core.notification import OnNext, OnError, OnCompleted
from .recorded import Recorded
from .subscription import Subscription


def is_prime(i: int) -> bool:
    """Tests if number is prime or not"""

    if i <= 1:
        return False

    _max = int(math.floor(math.sqrt(i)))
    for j in range(2, _max+1):
        if not i % j:
            return False

    return True


# New predicate tests
class OnNextPredicate:
    def __init__(self, predicate) -> None:
        self.predicate = predicate

    def __eq__(self, other):
        if other == self:
            return True
        if other is None:
            return False
        if other.kind != 'N':
            return False
        return self.predicate(other.value)


class OnErrorPredicate:
    def __init__(self, predicate):
        self.predicate = predicate

    def __eq__(self, other):
        if other == self:
            return True
        if other is None:
            return False
        if other.kind != 'E':
            return False
        return self.predicate(other.exception)


class ReactiveTest:
    created = 100
    subscribed = 200
    disposed = 1000

    @staticmethod
    def on_next(ticks: int, value: Any) -> Recorded:
        if isinstance(value, types.FunctionType):
            return Recorded(ticks, OnNextPredicate(value))

        return Recorded(ticks, OnNext(value))

    @staticmethod
    def on_error(ticks: int, exception: Exception) -> Recorded:
        if isinstance(exception, types.FunctionType):
            return Recorded(ticks, OnErrorPredicate(exception))

        return Recorded(ticks, OnError(exception))

    @staticmethod
    def on_completed(ticks: int) -> Recorded:
        return Recorded(ticks, OnCompleted())

    @staticmethod
    def subscribe(start: int, end: int) -> Subscription:
        return Subscription(start, end)
