from typing import Any, Optional

import rx
from rx import operators as ops
from rx.core import Observable


def _repeat_value(value: Any = None, repeat_count: Optional[int] = None) -> Observable:
    """Generates an observable sequence that repeats the given element
    the specified number of times.

    Examples:
        1 - res = repeat_value(42)
        2 - res = repeat_value(42, 4)

    Args:
        value: Element to repeat.
        repeat_count: [Optional] Number of times to repeat the element.
            If not specified, repeats indefinitely.

    Returns:
        An observable sequence that repeats the given element the
        specified number of times.
    """

    if repeat_count == -1:
        repeat_count = None

    xs = rx.return_value(value)
    return xs.pipe(ops.repeat(repeat_count))
