import asyncio
from asyncio import Future
from collections.abc import Callable
from typing import TypeVar, cast

from reactivex import Observable, abc
from reactivex.internal.exceptions import SequenceContainsNoElementsError

_T = TypeVar("_T")


def to_future_(
    future_ctor: Callable[[], Future[_T]] | None = None,
    scheduler: abc.SchedulerBase | None = None,
) -> Callable[[Observable[_T]], Future[_T]]:
    def to_future(source: Observable[_T]) -> Future[_T]:
        """Converts an existing observable sequence to a Future.

        If the observable emits a single item, then this item is set as the
        result of the future. If the observable emits a sequence of items, then
        the last emitted item is set as the result of the future.

        Example:
            future = reactivex.return_value(42).pipe(ops.to_future(asyncio.Future))

        Args:
            future_ctor: [Optional] The constructor of the future.

        Returns:
            A future with the last value from the observable sequence.
        """
        if future_ctor is not None:
            future_ctor_ = future_ctor
        else:
            try:
                future_ctor_ = asyncio.get_running_loop().create_future
            except RuntimeError:

                def create_future() -> Future[_T]:
                    return Future()  # Explicitly using Future[_T]

                future_ctor_ = create_future  # If no running loop

        future: Future[_T] = future_ctor_()

        has_value = False
        last_value: _T | None = None

        def on_next(value: _T) -> None:
            nonlocal last_value
            nonlocal has_value
            last_value = value
            has_value = True

        def on_error(err: Exception) -> None:
            if not future.cancelled():
                future.set_exception(err)

        def on_completed() -> None:
            nonlocal last_value
            if not future.cancelled():
                if has_value:
                    future.set_result(cast(_T, last_value))
                else:
                    future.set_exception(SequenceContainsNoElementsError())
            last_value = None

        dis = source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)
        future.add_done_callback(lambda _: dis.dispose())

        return future

    return to_future


__all__ = ["to_future_"]
