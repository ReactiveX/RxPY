from typing import Callable, Optional, TypeVar, Union, cast

from rx import operators as ops
from rx.core import ConnectableObservable, Observable, abc
from rx.core.typing import Mapper
from rx.subject import BehaviorSubject

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
