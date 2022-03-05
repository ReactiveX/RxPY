from asyncio import Future
from typing import Callable, TypeVar, Union

import reactivex
from reactivex import Observable, abc

_T = TypeVar("_T")


def if_then_(
    condition: Callable[[], bool],
    then_source: Union[Observable[_T], "Future[_T]"],
    else_source: Union[None, Observable[_T], "Future[_T]"] = None,
) -> Observable[_T]:
    """Determines whether an observable collection contains values.

    Example:
    1 - res = reactivex.if_then(condition, obs1)
    2 - res = reactivex.if_then(condition, obs1, obs2)

    Args:
        condition: The condition which determines if the then_source or
            else_source will be run.
        then_source: The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source: [Optional] The observable sequence or
            Promise that will be run if the condition function returns
            False. If this is not provided, it defaults to
            reactivex.empty

    Returns:
        An observable sequence which is either the then_source or
        else_source.
    """

    else_source_: Union[Observable[_T], "Future[_T]"] = else_source or reactivex.empty()

    then_source = (
        reactivex.from_future(then_source)
        if isinstance(then_source, Future)
        else then_source
    )
    else_source_ = (
        reactivex.from_future(else_source_)
        if isinstance(else_source_, Future)
        else else_source_
    )

    def factory(_: abc.SchedulerBase) -> Union[Observable[_T], "Future[_T]"]:
        return then_source if condition() else else_source_

    return reactivex.defer(factory)


__all__ = ["if_then_"]
