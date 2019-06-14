from typing import Callable, Optional, Union
from asyncio import Future

from rx import throw, from_future
from rx.core import Observable, typing
from rx.internal.utils import is_future


def _defer(factory: Callable[[typing.Scheduler], Union[Observable, Future]]
           ) -> Observable:
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
        >>> res = defer(lambda: of(1, 2, 3))

    Args:
        factory: Observable factory function to invoke for each
        observer that subscribes to the resulting sequence.

    Returns:
        An observable sequence whose observers trigger an invocation
        of the given observable factory function.
    """

    def subscribe_observer(observer: typing.Observer,
                           scheduler: Optional[typing.Scheduler] = None
                           ) -> typing.Disposable:
        try:
            result = factory(scheduler)
        except Exception as ex:  # By design. pylint: disable=W0703
            return observer.subscribe_to(throw(ex))

        result = from_future(result) if is_future(result) else result
        return observer.subscribe_to(result, scheduler=scheduler)
    return Observable(subscribe_observer=subscribe_observer)
