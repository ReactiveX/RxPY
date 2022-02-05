from typing import Callable, TypeVar

import rx
from rx.core import Observable

_T = TypeVar("_T")


def on_error_resume_next_(
    second: Observable[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    def on_error_resume_next(source: Observable[_T]) -> Observable[_T]:
        return rx.on_error_resume_next(source, second)

    return on_error_resume_next


__all__ = ["on_error_resume_next_"]
