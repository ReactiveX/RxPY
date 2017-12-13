from typing import Any, Callable

from rx.core import Observable, AnonymousObservable
from rx.core import bases


def defer(observable_factory: Callable[[bases.Scheduler], Observable]) -> Observable:
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
    1 - res = rx.Observable.defer(lambda: rx.Observable.from_([1,2,3]))

    Keyword arguments:
    :param types.FunctionType observable_factory: Observable factory function
        to invoke for each observer that subscribes to the resulting sequence.

    Returns an observable sequence whose observers trigger an invocation
    of the given observable factory function.
    """

    def subscribe(observer, scheduler=None):
        try:
            result = observable_factory(scheduler)
        except Exception as ex:
            return Observable.throw_exception(ex).subscribe(observer)

        result = Observable.from_future(result)
        return result.subscribe(observer, scheduler)
    return AnonymousObservable(subscribe)
