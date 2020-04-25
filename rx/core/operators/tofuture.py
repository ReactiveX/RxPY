from typing import Callable, Optional
from asyncio import Future

from .. import typing
from rx.core import Observable
from rx.internal.exceptions import SequenceContainsNoElementsError


def _to_future(future_ctor: Optional[Callable[[], Future]] = None,
               scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Future]:
    future_ctor = future_ctor or Future
    future = future_ctor()

    def to_future(source: Observable) -> Future:
        """Converts an existing observable sequence to a Future.

        If the observable emits a single item, then this item is set as the
        result of the future. If the observable emits a sequence of items, then
        the last emitted item is set as the result of the future.

        Example:
            future = rx.return_value(42).pipe(ops.to_future(asyncio.Future))

        Args:
            future_ctor: [Optional] The constructor of the future.

        Returns:
            A future with the last value from the observable sequence.
        """

        has_value = False
        last_value = None

        def on_next(value):
            nonlocal last_value
            nonlocal has_value
            last_value = value
            has_value = True

        def on_error(err):
            future.set_exception(err)

        def on_completed():
            nonlocal last_value
            if has_value:
                future.set_result(last_value)
            else:
                future.set_exception(SequenceContainsNoElementsError())
            last_value = None

        source.subscribe_(on_next, on_error, on_completed, scheduler=scheduler)

        # No cancellation can be done
        return future
    return to_future
