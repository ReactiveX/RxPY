from typing import Callable, Union, cast, TypeVar

import rx
from rx.core import Observable, abc, typing

_T = TypeVar("_T")


def _if_then(
    condition: Callable[[], bool],
    then_source: Union[Observable[_T], typing.Future],
    else_source: Union[None, Observable[_T], typing.Future] = None,
) -> Observable[_T]:
    """Determines whether an observable collection contains values.

    Example:
    1 - res = rx.if_then(condition, obs1)
    2 - res = rx.if_then(condition, obs1, obs2)

    Args:
        condition: The condition which determines if the then_source or
            else_source will be run.
        then_source: The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source: [Optional] The observable sequence or
            Promise that will be run if the condition function returns
            False. If this is not provided, it defaults to
            rx.empty

    Returns:
        An observable sequence which is either the then_source or
        else_source.
    """

    else_source = else_source or rx.empty()

    then_source = (
        rx.from_future(cast(typing.Future, then_source)) if isinstance(then_source, typing.Future) else then_source
    )
    else_source = (
        rx.from_future(cast(typing.Future, else_source)) if isinstance(else_source, typing.Future) else else_source
    )

    def factory(_: abc.SchedulerBase) -> Observable[_T]:
        return then_source if condition() else else_source

    return rx.defer(factory)
