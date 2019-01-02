from rx.core import Observable, StaticObservable


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
        return StaticObservable.throw(ex)

    return StaticObservable.from_future(future)
