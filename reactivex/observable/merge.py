from typing import TypeVar

import reactivex
from reactivex import Observable
from reactivex import operators as ops

_T = TypeVar("_T")


def merge_(*sources: Observable[_T]) -> Observable[_T]:
    return reactivex.from_iterable(sources).pipe(ops.merge_all())


__all__ = ["merge_"]
