from typing import Callable

import rx
from rx import operators as ops
from rx.core import Observable, GroupedObservable


def _group_by(key_mapper, element_mapper=None) -> Callable[[Observable], Observable]:
    def duration_mapper(_):
        return rx.never()

    return ops.group_by_until(key_mapper, element_mapper, duration_mapper)
