from typing import TypeVar, Callable, Optional

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Comparer
from rx.internal.basic import default_comparer

_T = TypeVar("_T")


def _contains(
    value: _T, comparer: Optional[Comparer[_T]] = None
) -> Callable[[Observable[_T]], Observable[bool]]:
    comparer_ = comparer or default_comparer

    filtering = ops.filter(lambda v: comparer_(v, value))
    something = ops.some()

    return pipe(filtering, something)


__all__ = ["_contains"]
