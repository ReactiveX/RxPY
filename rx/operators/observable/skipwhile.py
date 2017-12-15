from typing import Any, Callable
from rx import Observable, AnonymousObservable


def skip_while(source: Observable, predicate: Callable[[Any], Any]) -> Observable:
    """Bypasses elements in an observable sequence as long as a specified
    condition is true and then returns the remaining elements. The
    element's index is used in the logic of the predicate function.

    1 - source.skip_while(lambda value: value < 10)

    predicate -- A function to test each element for a condition; the
        second parameter of the function represents the index of the
        source element.

    Returns an observable sequence that contains the elements from the
    input sequence starting at the first element in the linear series that
    does not pass the test specified by predicate.
    """

    def subscribe(observer, scheduler=None):
        running = False

        def send(value):
            nonlocal running

            if not running:
                try:
                    running = not predicate(value)
                except Exception as exn:
                    observer.throw(exn)
                    return

            if running:
                observer.send(value)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)


def skip_while_indexed(source: Observable, predicate: Callable[[Any, int], Any]) -> Observable:
    """Bypasses elements in an observable sequence as long as a specified
    condition is true and then returns the remaining elements. The
    element's index is used in the logic of the predicate function.

    1 - source.skip_while(lambda value, index: value < 10 or index < 10)

    predicate -- A function to test each element for a condition; the
        second parameter of the function represents the index of the
        source element.

    Returns an observable sequence that contains the elements from the
    input sequence starting at the first element in the linear series that
    does not pass the test specified by predicate.
    """

    def subscribe(observer, scheduler=None):
        i, running = 0, False

        def send(value):
            nonlocal i, running

            if not running:
                try:
                    running = not predicate(value, i)
                except Exception as exn:
                    observer.throw(exn)
                    return
                else:
                    i += 1

            if running:
                observer.send(value)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
