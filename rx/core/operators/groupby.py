from typing import Callable, Optional

import rx
from rx import operators as ops
from rx.core import Observable
from rx.core.typing import Mapper
from rx.subject import Subject


def _group_by(key_mapper: Mapper,
              element_mapper: Optional[Mapper] = None,
              subject_mapper: Optional[Callable[[], Subject]] = None,
              ) -> Callable[[Observable], Observable]:

    def duration_mapper(_):
        return rx.never()

    return ops.group_by_until(key_mapper, element_mapper, duration_mapper, subject_mapper)
