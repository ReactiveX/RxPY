from typing import Callable
from rx.core import ObservableBase, Observable
from rx.core import abc


def if_then(condition: Callable[[], bool], then_source: ObservableBase,
            else_source: ObservableBase = None) -> ObservableBase:
    """Determines whether an observable collection contains values.

    Example:
    1 - res = rx.Observable.if(condition, obs1)
    2 - res = rx.Observable.if(condition, obs1, obs2)

    Keyword parameters:
    condition -- The condition which determines if the then_source or
        else_source will be run.
    then_source -- The observable sequence or Promise that
        will be run if the condition function returns true.
    else_source -- [Optional] The observable sequence or
        Promise that will be run if the condition function returns
        False. If this is not provided, it defaults to
        rx.Observable.empty

    Returns an observable sequence which is either the
    then_source or else_source.
    """

    else_source = else_source or Observable.empty()

    then_source = Observable.from_future(then_source)
    else_source = Observable.from_future(else_source)

    def factory(_: abc.Scheduler):
        return then_source if condition() else else_source

    return Observable.defer(factory)
