from typing import Callable, TypeVar

from reactivex import Observable, operators
from reactivex.typing import Mapper

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def concatmap_(
    project: Mapper[_T1, Observable[_T2]]
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    def _concat_map(source: Observable[_T1]) -> Observable[_T2]:
        return source.pipe(operators.map(project), operators.merge(max_concurrent=1))

    return _concat_map


__all__ = ["concatmap_"]
