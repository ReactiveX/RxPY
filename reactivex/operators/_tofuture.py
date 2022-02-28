import asyncio
from asyncio import Future
from typing import Callable, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.internal.exceptions import SequenceContainsNoElementsError

_T = TypeVar("_T")


def to_future_(
    future_ctor: Optional[Callable[[], "Future[_T]"]] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], "Future[_T]"]:
    future_ctor_: Callable[[], "Future[_T]"] = (
        future_ctor or asyncio.get_event_loop().create_future
    )
    future: "Future[_T]" = future_ctor_()

    def to_future(source: Observable[_T]) -> "Future[_T]":
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

        has_value = False
        last_value = cast(_T, None)

        def on_next(value: _T):
            nonlocal last_value
            nonlocal has_value
            last_value = value
            has_value = True

        def on_error(err: Exception):
            if not future.cancelled():
                future.set_exception(err)

        def on_completed():
            nonlocal last_value
            if not future.cancelled():
                if has_value:
                    future.set_result(last_value)
                else:
                    future.set_exception(SequenceContainsNoElementsError())
            last_value = None

        dis = source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)
        future.add_done_callback(lambda _: dis.dispose())

        return future

    return to_future


__all__ = ["to_future_"]
