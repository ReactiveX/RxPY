from typing import Any, Callable

from reactivex import Observable, compose
from reactivex import operators as ops


def is_empty_() -> Callable[[Observable[Any]], Observable[bool]]:
    """Determines whether an observable sequence is empty.

    Returns:
        An observable sequence containing a single element
        determining whether the source sequence is empty.
    """

    def mapper(b: bool) -> bool:
        return not b

    return compose(
        ops.some(),
        ops.map(mapper),
    )


__all__ = ["is_empty_"]
