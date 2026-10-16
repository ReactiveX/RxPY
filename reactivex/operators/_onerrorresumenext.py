from collections.abc import Callable
from typing import TypeVar

import reactivex
from reactivex import Observable

_T = TypeVar("_T")


def on_error_resume_next_(
    second: Observable[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    def on_error_resume_next(source: Observable[_T]) -> Observable[_T]:
        """Continues an observable sequence that is terminated normally or
        by an exception with the next observable sequence.

        Args:
            source: First observable sequence.

        Returns:
            An observable sequence that concatenates the source and second
            sequences, even if the source sequence terminates exceptionally.
        """
        return reactivex.on_error_resume_next(source, second)

    return on_error_resume_next


__all__ = ["on_error_resume_next_"]
