from typing import Callable, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate

_T = TypeVar("_T")


def all_(predicate: Predicate[_T]) -> Callable[[Observable[_T]], Observable[bool]]:
    def filter(v: _T):
        return not predicate(v)

    def mapping(b: bool) -> bool:
        return not b

    return pipe(
        ops.filter(filter),
        ops.some(),
        ops.map(mapping),
    )


__all__ = ["all_"]
