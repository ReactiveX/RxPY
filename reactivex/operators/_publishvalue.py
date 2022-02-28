from typing import Callable, Optional, TypeVar, Union, cast

from reactivex import ConnectableObservable, Observable, abc
from reactivex import operators as ops
from reactivex.subject import BehaviorSubject
from reactivex.typing import Mapper

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def publish_value_(
    initial_value: _T1,
    mapper: Optional[Mapper[Observable[_T1], Observable[_T2]]] = None,
) -> Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]:
    if mapper:

        def subject_factory(
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> BehaviorSubject[_T1]:
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)

    subject = BehaviorSubject(cast(_T2, initial_value))
    return ops.multicast(subject)


__all__ = ["publish_value_"]
