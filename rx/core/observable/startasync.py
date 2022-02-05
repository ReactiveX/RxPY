from asyncio import Future
from typing import Callable, TypeVar

from rx import from_future, throw
from rx.core import Observable

_T = TypeVar("_T")


def start_async_(function_async: Callable[[], "Future[_T]"]) -> Observable[_T]:
    try:
        future = function_async()
    except Exception as ex:  # pylint: disable=broad-except
        return throw(ex)

    return from_future(future)


__all__ = ["start_async_"]
