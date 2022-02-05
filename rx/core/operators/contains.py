from typing import TypeVar, Callable, Optional

from rx import operators as ops
from rx.core import Observable, pipe, typing
from rx.internal.basic import default_comparer

_T = TypeVar("_T")


def contains_(
    value: _T, comparer: Optional[typing.Comparer[_T]] = None
) -> Callable[[Observable[_T]], Observable[bool]]:
    comparer_ = comparer or default_comparer

    filtering = ops.filter(lambda v: comparer_(v, value))
    something = ops.some()

    return pipe(filtering, something)


__all__ = ["contains_"]
