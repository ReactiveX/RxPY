from typing import TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def concat_all_(source: Observable[Observable[_T]]) -> Observable[_T]:
    """Flatten inner observables one at a time, in source order."""
    return source.pipe(ops.merge(max_concurrent=1))


__all__ = ["concat_all_"]
