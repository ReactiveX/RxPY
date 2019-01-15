from typing import Any, Callable

from rx import operators as ops
from rx.core import Observable
from rx.subjects import BehaviorSubject
from rx.core.typing import Mapper


def _publish_value(initial_value: Any, mapper: Mapper = None) -> Callable[[Observable], Observable]:
    if mapper:
        def subject_factory(scheduler):
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)
    return ops.multicast(BehaviorSubject(initial_value))
