from asyncio import Future
from typing import Callable

from rx import from_future, throw
from rx.core import Observable


def _start_async(function_async: Callable[[], Future]) -> Observable:
    try:
        future = function_async()
    except Exception as ex:  # pylint: disable=broad-except
        return throw(ex)

    return from_future(future)
