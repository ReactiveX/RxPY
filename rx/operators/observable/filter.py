from typing import Any, Callable
from rx.core import ObservableBase, AnonymousObservable


def filter(predicate: Callable[[Any], bool], source: ObservableBase):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value: value < 10)

    Keyword arguments:
    :param Observable self: Observable sequence to filter.
    :param A function to test each source element
        for a condition; the
        second parameter of the function represents the index of the source
        element.

    :returns: An observable sequence that contains elements from the input
    sequence that satisfy the condition.
    :rtype: Observable
    """

    def subscribe(observer, scheduler=None):
        def send(value):
            try:
                should_run = predicate(value)
            except Exception as ex:  # By design. pylint: disable=W0703
                observer.throw(ex)
                return

            if should_run:
                observer.send(value)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)


def filter_indexed(predicate: Callable[[Any, int], bool], source: ObservableBase):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value, index: value < 10 or index < 10)

    Keyword arguments:
    :param source: Observable sequence to filter.
    :param predicate: A function to test each source element
        for a condition; the
        second parameter of the function represents the index of the source
        element.

    :returns: An observable sequence that contains elements from the input
    sequence that satisfy the condition.
    :rtype: Observable
    """

    def subscribe(observer, scheduler=None):
        count = 0

        def send(value):
            nonlocal count

            try:
                should_run = predicate(value, count)
            except Exception as ex:  # By design. pylint: disable=W0703
                observer.throw(ex)
                return
            else:
                count += 1

            if should_run:
                observer.send(value)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
