from typing import Callable

from rx.core import Observable, ObservableBase, AnonymousObservable
from rx.core import abc
from rx.internal.utils import is_future


def defer(observable_factory: Callable[[abc.Scheduler], ObservableBase]) -> ObservableBase:
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
        >>> res = rx.Observable.defer(lambda: rx.Observable.of(1, 2, 3))

    Args:
        observable_factory: Observable factory function to invoke for
        each observer that subscribes to the resulting sequence.

    Returns:
        An observable sequence whose observers trigger an invocation
        of the given observable factory function.
    """

    def subscribe(observer, scheduler=None):
        try:
            result = observable_factory(scheduler)
        except Exception as ex:
            return Observable.throw(ex).subscribe(observer)

        result = Observable.from_future(result) if is_future(result) else result
        return result.subscribe(observer, scheduler)
    return AnonymousObservable(subscribe)
