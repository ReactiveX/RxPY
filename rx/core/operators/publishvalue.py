from typing import Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc
from rx.core.typing import Mapper
from rx.subject import BehaviorSubject

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def publish_value_(
    initial_value: _T1, mapper: Optional[Mapper[_T1, _T2]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    if mapper:

        def subject_factory(scheduler: abc.SchedulerBase) -> BehaviorSubject[_T1]:
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)
    return ops.multicast(BehaviorSubject(initial_value))


__all__ = ["publish_value_"]
