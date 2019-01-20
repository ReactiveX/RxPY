from typing import Callable

from rx import operators as ops
from rx.core import Observable, pipe, typing


def _buffer_with_time(timespan: typing.RelativeTime, timeshift: typing.RelativeTime = None,
                      scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    if not timeshift:
        timeshift = timespan

    return pipe(
        ops.window_with_time(timespan, timeshift, scheduler),
        ops.flat_map(lambda x: x.pipe(ops.to_iterable()))
    )
