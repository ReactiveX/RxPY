from typing import Callable, Union
from asyncio import Future

from rx import throw, from_future
from rx.core import Observable
from rx.core.typing import Scheduler
from rx.internal.utils import is_future


def _defer(factory: Callable[[Scheduler], Union[Observable, Future]]
           ) -> Observable:
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

    def subscribe(observer, scheduler=None):
        try:
            result = factory(scheduler)
        except Exception as ex:  # By design. pylint: disable=W0703
            return throw(ex).subscribe(observer)

        result = from_future(result) if is_future(result) else result
        return result.subscribe(observer, scheduler=scheduler)
    return Observable(subscribe)
