from typing import Callable

from rx import operators as ops
from rx.core import Observable, pipe


def _buffer_with_time(timespan, timeshift=None) -> Callable[[Observable], Observable]:
    if not timeshift:
        timeshift = timespan

    return pipe(
        ops.window_with_time(timespan, timeshift),
        ops.flat_map(lambda x: x.pipe(ops.to_iterable()))
    )
