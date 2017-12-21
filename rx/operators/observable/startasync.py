from rx.core import ObservableBase, Observable


def start_async(function_async) -> ObservableBase:
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
        return Observable.throw(ex)

    return Observable.from_future(future)
