from typing import Callable
from asyncio import Future

from rx.core import Observable


def _to_future(future_ctor: Callable[[], Future] = None) -> Callable[[Observable], Future]:
    future_ctor = future_ctor or Future
    future = future_ctor()

    def to_future(source: Observable) -> Future:
        """Converts an existing observable sequence to a Future.

        Example:
            future = rx.return_value(42).pipe(ops.to_future(asyncio.Future))

        Args:
            future_ctor: [Optional] The constructor of the future.

        Returns:
            A future with the last value from the observable sequence.
        """

        has_value = []

        def on_next(value):
            has_value.append(value)

        def on_error(err):
            future.set_exception(err)

        def on_completed():
            if has_value:
                future.set_result(has_value.pop())

        source.subscribe_(on_next, on_error, on_completed)

        # No cancellation can be done
        return future
    return to_future
