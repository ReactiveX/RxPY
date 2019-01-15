from rx import throw, from_future
from rx.core import Observable


def _start_async(function_async) -> Observable:
    try:
        future = function_async()
    except Exception as ex:  # pylint: disable=broad-except
        return throw(ex)

    return from_future(future)
