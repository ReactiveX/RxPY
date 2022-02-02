from typing import Callable, Optional, Union, TypeVar

from rx import from_future, throw
from rx.core import Observable, abc, typing
from rx.scheduler import ImmediateScheduler

_T = TypeVar("_T")


def _defer(factory: Callable[[abc.SchedulerBase], Union[Observable[_T], typing.Future]]) -> Observable[_T]:
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
        >>> res = defer(lambda: of(1, 2, 3))

    Args:
        observable_factory: Observable factory function to invoke for
        each observer that subscribes to the resulting sequence.

    Returns:
        An observable sequence whose observers trigger an invocation
        of the given observable factory function.
    """

    def subscribe(observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None) -> abc.DisposableBase:
        try:
            result = factory(scheduler or ImmediateScheduler.singleton())
        except Exception as ex:  # By design. pylint: disable=W0703
            return throw(ex).subscribe(observer)

        result = from_future(result) if isinstance(result, typing.Future) else result
        return result.subscribe(observer, scheduler=scheduler)

    return Observable(subscribe)
