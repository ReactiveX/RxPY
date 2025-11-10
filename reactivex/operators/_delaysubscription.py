from typing import Any, TypeVar

import reactivex
from reactivex import Observable, abc, typing
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def delay_subscription_(
    source: Observable[_T],
    duetime: typing.AbsoluteOrRelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Time shifts the observable sequence by delaying the subscription.

    Examples:
        >>> source.pipe(delay_subscription(5))
        >>> delay_subscription(5)(source)

    Args:
        source: Source subscription to delay.
        duetime: Time to delay subscription.
        scheduler: Scheduler to use for timing.

    Returns:
        Time-shifted sequence.
    """

    def mapper(_: Any) -> Observable[_T]:
        return reactivex.empty()

    return source.pipe(
        ops.delay_with_mapper(reactivex.timer(duetime, scheduler=scheduler), mapper)
    )


__all__ = ["delay_subscription_"]
