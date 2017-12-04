from typing import Callable, Any
from rx import Observable, AnonymousObservable


def map(source: Observable, mapper: Callable[[Any], Any]) -> Observable:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    1 - source.map(lambda value: value * value)

    Keyword arguments:
    :param Callable[[Any, Any], Any] mapper: A transform function to
        apply to each source element; the second parameter of the
        function represents the index of the source element.
    :rtype: Observable

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of source.
    """

    def subscribe(observer):
        def on_next(value):
            try:
                result = mapper(value)
            except Exception as err:
                observer.on_error(err)
            else:
                observer.on_next(result)

        return source.subscribe(on_next,
                                observer.on_error,
                                observer.on_completed)
    return AnonymousObservable(subscribe)
