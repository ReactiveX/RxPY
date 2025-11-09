from collections.abc import Callable
from typing import TypeVar

from reactivex import ConnectableObservable, Observable, abc
from reactivex import operators as ops
from reactivex.subject import BehaviorSubject
from reactivex.typing import Mapper

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def publish_value_(
    initial_value: _T1,
    mapper: Mapper[Observable[_T1], Observable[_T2]] | None = None,
) -> (
    Callable[[Observable[_T1]], ConnectableObservable[_T1]]
    | Callable[[Observable[_T1]], Observable[_T2]]
):
    if mapper:

        def subject_factory(
            scheduler: abc.SchedulerBase | None = None,
        ) -> BehaviorSubject[_T1]:
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)

    subject = BehaviorSubject(initial_value)
    return ops.multicast(subject)


__all__ = ["publish_value_"]
