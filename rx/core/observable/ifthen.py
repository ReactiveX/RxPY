from typing import Callable, Optional

import rx
from rx.core import abc
from rx.core import Observable
from rx.internal.utils import is_future


def _if_then(condition: Callable[[], bool], then_source: Observable,
             else_source: Optional[Observable] = None) -> Observable:
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

    then_source = rx.from_future(then_source) if is_future(then_source) else then_source
    else_source = rx.from_future(else_source) if is_future(else_source) else else_source

    def factory(_: abc.Scheduler):
        return then_source if condition() else else_source

    return rx.defer(factory)
