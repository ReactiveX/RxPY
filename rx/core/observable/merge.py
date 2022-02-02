from typing import TypeVar
import rx
from rx import operators as ops
from rx.core import Observable

_T = TypeVar("_T")


def _merge(*sources: Observable[_T]) -> Observable[_T]:
    return rx.from_iterable(sources).pipe(ops.merge_all())


__all__ = ["_merge"]
