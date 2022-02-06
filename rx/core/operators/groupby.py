from typing import Any, Callable, Optional, TypeVar

import rx
from rx import operators as ops
from rx.core import Observable
from rx.core.observable.groupedobservable import GroupedObservable
from rx.core.typing import Mapper
from rx.subject import Subject

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


def _group_by(
    key_mapper: Mapper[_T, _TKey],
    element_mapper: Optional[Mapper[_T, _TValue]] = None,
    subject_mapper: Optional[Callable[[], Subject[_TValue]]] = None,
) -> Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]:
    def duration_mapper(_: GroupedObservable[Any, Any]) -> Observable[Any]:
        return rx.never()

    return ops.group_by_until(
        key_mapper, element_mapper, duration_mapper, subject_mapper
    )


__all__ = ["_group_by"]
