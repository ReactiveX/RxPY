import collections
from typing import Any, Callable
from rx.core import Observable, ObservableBase


def _flat_map(source, selector):
    def projection(x):
        selector_result = selector(x)
        if isinstance(selector_result, collections.Iterable):
            result = Observable.from_(selector_result)
        else:
            result = Observable.from_future(selector_result)
        return result

    return source.map(projection).merge_all()


def _flat_map_indexed(source, selector):
    def projection(x, i):
        selector_result = selector(x, i)
        if isinstance(selector_result, collections.Iterable):
            result = Observable.from_(selector_result)
        else:
            result = Observable.from_future(selector_result)
        return result

    return source.map_indexed(projection).merge_all()


def flat_map(source: ObservableBase, selector: Callable[[Any], Any],
             result_selector: Callable=None) -> ObservableBase:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of an observable sequence to an observable
    sequence, invokes the result selector for the source element and each
    of the corresponding inner sequence's elements, and merges the results
    into one observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x), lambda x, y: x + y)

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences into
    one observable sequence.

    1 - source.flat_map(Observable.from_([1,2,3]))

    Keyword arguments:
    selector -- A transform function to apply to each element or an
        observable sequence to project each element from the source
        sequence onto.
    result_selector -- [Optional] A transform function to apply to each
        element of the intermediate sequence.

    Returns an observable sequence whose elements are the result of
    invoking the one-to-many transform function collectionSelector on each
    element of the input sequence and then mapping each of those sequence
    elements and their corresponding source element to a result element.
    """

    if result_selector:
        def projection(x):
            selector_result = selector(x)
            if isinstance(selector_result, collections.Iterable):
                result = Observable.from_(selector_result)
            else:
                result = Observable.from_future(selector_result)
            return result.map(lambda y: result_selector(x, y))

        return source.flat_map(projection)

    if callable(selector):
        ret = _flat_map(source, selector)
    else:
        ret = _flat_map(source, lambda _: selector)

    return ret


def flat_map_indexed(source: Observable, selector: Callable[[Any, int], Any],
                     result_selector: Callable=None) -> ObservableBase:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of an observable sequence to an observable
    sequence, invokes the result selector for the source element and each
    of the corresponding inner sequence's elements, and merges the results
    into one observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x), lambda x, y: x + y)

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences into
    one observable sequence.

    1 - source.flat_map(Observable.from_([1,2,3]))

    Keyword arguments:
    selector -- A transform function to apply to each element or an
        observable sequence to project each element from the source
        sequence onto.
    result_selector -- [Optional] A transform function to apply to each
        element of the intermediate sequence.

    Returns an observable sequence whose elements are the result of
    invoking the one-to-many transform function collectionSelector on each
    element of the input sequence and then mapping each of those sequence
    elements and their corresponding source element to a result element.
    """

    if result_selector:
        def projection(x, i):
            selector_result = selector(x, i)
            if isinstance(selector_result, collections.Iterable):
                result = Observable.from_(selector_result)
            else:
                result = Observable.from_future(selector_result)
            return result.map_indexed(lambda y, i: result_selector(x, y, i))

        return source.flat_map_indexed(projection)

    if callable(selector):
        ret = _flat_map_indexed(source, selector)
    else:
        ret = _flat_map_indexed(source, lambda _, __: selector)

    return ret
