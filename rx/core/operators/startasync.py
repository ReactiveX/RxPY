from rx import throw, from_future
from rx.core import Observable


def start_async(function_async) -> Observable:
    """Invokes the asynchronous function, surfacing the result through
    an observable sequence.

    Keyword arguments:
    function_async -- Asynchronous function which returns a Future to
        run.

    Returns an observable sequence exposing the function's result value,
    or an exception.
    """

    try:
        future = function_async()
    except Exception as ex:
        return throw(ex)

    return from_future(future)
