from typing import Any, Callable

from rx.core import Observable, AnonymousObservable


def take_while(source: Observable, predicate: Callable[[Any], Any]) -> Observable:
    """Returns elements from an observable sequence as long as a specified
    condition is true. The element's index is used in the logic of the
    predicate function.

    1 - source.take_while(lambda value: value < 10)

    Keyword arguments:
    predicate -- A function to test each element for a condition; the
        second parameter of the function represents the index of the source
        element.

    Returns an observable sequence that contains the elements from the
    input sequence that occur before the element at which the test no
    longer passes.
    """

    def subscribe(observer, scheduler=None):
        running = True

        def send(value):
            nonlocal running

            with source.lock:
                if not running:
                    return

                try:
                    running = predicate(value)
                except Exception as exn:
                    observer.throw(exn)
                    return

            if running:
                observer.send(value)
            else:
                observer.close()

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)


def take_while_indexed(source: Observable, predicate: Callable[[Any, int], Any]) -> Observable:
    """Returns elements from an observable sequence as long as a specified
    condition is true. The element's index is used in the logic of the
    predicate function.

    1 - source.take_while(lambda value, index: value < 10 or index < 10)

    Keyword arguments:
    predicate -- A function to test each element for a condition; the
        second parameter of the function represents the index of the source
        element.

    Returns an observable sequence that contains the elements from the
    input sequence that occur before the element at which the test no
    longer passes.
    """

    def subscribe(observer, scheduler=None):
        running, i = True, 0

        def send(value):
            nonlocal running, i
            with source.lock:
                if not running:
                    return

                try:
                    running = predicate(value, i)
                except Exception as exn:
                    observer.throw(exn)
                    return
                else:
                    i += 1

            if running:
                observer.send(value)
            else:
                observer.close()

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
