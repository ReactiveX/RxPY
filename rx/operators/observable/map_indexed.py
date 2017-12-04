from typing import Callable, Any

from rx import Observable, AnonymousObservable
from rx.internal.utils import adapt_call
from rx.internal import extensionmethod


def map_indexed(source: Observable, selector: Callable[[Any, int], Any]) -> Observable:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    1 - source.map(lambda value, index: value * value + index)

    Keyword arguments:
    :param Callable[[Any, Any], Any] selector: A transform function to
        apply to each source element; the second parameter of the
        function represents the index of the source element.
    :rtype: Observable

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of source.
    """

    def subscribe(observer):
        count = 0

        def on_next(value):
            nonlocal count

            try:
                result = selector(value, count)
            except Exception as err:
                observer.on_error(err)
            else:
                count += 1
                observer.on_next(result)

        return source.subscribe(on_next, observer.on_error, observer.on_completed)
    return AnonymousObservable(subscribe)
