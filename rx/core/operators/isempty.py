from typing import Any, Callable

from rx import operators as ops
from rx.core import Observable, pipe


def is_empty_() -> Callable[[Observable[Any]], Observable[bool]]:
    """Determines whether an observable sequence is empty.

    Returns:
        An observable sequence containing a single element
        determining whether the source sequence is empty.
    """

    return pipe(ops.some(), ops.map(lambda b: not b))


__all__ = ["is_empty_"]
