from typing import Any, Callable, Optional, TypeVar

import rx
from rx import operators as ops
from rx.core import Observable, abc, typing

_T = TypeVar("_T")


def delay_subscription_(
    duetime: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def delay_subscription(source: Observable[_T]) -> Observable[_T]:
        """Time shifts the observable sequence by delaying the subscription.

        Exampeles.
            >>> res = source.delay_subscription(5)

        Args:
            source: Source subscription to delay.

        Returns:
            Time-shifted sequence.
        """

        def mapper(_: Any) -> Observable[_T]:
            return rx.empty()

        return source.pipe(
            ops.delay_with_mapper(rx.timer(duetime, scheduler=scheduler), mapper)
        )

    return delay_subscription


__all__ = ["delay_subscription_"]
