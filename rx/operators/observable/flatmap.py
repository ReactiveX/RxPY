import collections
from typing import Any, Callable
from rx.core import Observable, ObservableBase
from rx.core.typing import Mapper, MapperIndexed
from rx.internal.utils import is_future


def _flat_map(source, mapper=None, mapper_indexed=None):
    def projection(x, i):
        mapper_result = mapper(x) if mapper else mapper_indexed(x, i)
        if isinstance(mapper_result, collections.abc.Iterable):
            result = Observable.from_(mapper_result)
        else:
            result = Observable.from_future(mapper_result) if is_future(
                mapper_result) else mapper_result
        return result

    return source.mapi(projection).merge_all()


def flat_map(source: ObservableBase,
             mapper: Mapper = None,
             result_mapper: Callable[[Any, Any], Any] = None,
             ) -> ObservableBase:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of an observable sequence to an observable
    sequence, invokes the result mapper for the source element and each
    of the corresponding inner sequence's elements, and merges the results
    into one observable sequence.

    1 - source.flat_map(lambda x: Observable.range(0, x), lambda x, y: x + y)

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences into
    one observable sequence.

    1 - source.flat_map(Observable.of(1, 2, 3))

    Keyword arguments:
    mapper -- A transform function to apply to each element or an
        observable sequence to project each element from the source
        sequence onto.
    result_mapper -- [Optional] A transform function to apply to each
        element of the intermediate sequence.
    result_mapper_indexed -- [Optional] A transform function to apply to each
        element of the intermediate sequence.

    Returns an observable sequence whose elements are the result of
    invoking the one-to-many transform function collectionSelector on each
    element of the input sequence and then mapping each of those sequence
    elements and their corresponding source element to a result element.
    """

    if result_mapper:
        def projection(x: Any, idx: int) -> Any:
            mapper_result = mapper(x)
            if isinstance(mapper_result, collections.abc.Iterable):
                result = Observable.from_(mapper_result)
            else:
                result = Observable.from_future(mapper_result) if is_future(
                    mapper_result) else mapper_result

            return result.map(lambda y: result_mapper(x, y))

        return source.flat_mapi(mapper_indexed=projection)

    if callable(mapper):
        ret = _flat_map(source, mapper=mapper)
    else:
        ret = _flat_map(source, mapper=lambda _: mapper)

    return ret


def flat_mapi(source: ObservableBase,
              mapper_indexed: MapperIndexed = None,
              result_mapper_indexed: Callable[[Any, Any, int], Any] = None
              ) -> ObservableBase:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    1 - source.flat_mapi(lambda x, i: Observable.range(0, x))

    Or:
    Projects each element of an observable sequence to an observable
    sequence, invokes the result mapper for the source element and each
    of the corresponding inner sequence's elements, and merges the results
    into one observable sequence.

    1 - source.flat_mapi(lambda x, i: Observable.range(0, x + 1), lambda x, y, i: x + y)

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences into
    one observable sequence.

    1 - source.flat_mapi(Observable.of(1, 2, 3))

    Keyword arguments:
    mapper_indexed -- [Optional] A transform function to apply to each
        element or an
        observable sequence to project each element from the source
        sequence onto.
    result_mapper_indexed -- [Optional] A transform function to apply to each
        element of the intermediate sequence.

    Returns an observable sequence whose elements are the result of
    invoking the one-to-many transform function collectionSelector on each
    element of the input sequence and then mapping each of those sequence
    elements and their corresponding source element to a result element.
    """

    if result_mapper_indexed:
        def projection(x: Any, idx: int) -> Any:
            mapper_result = mapper_indexed(x, idx)
            if isinstance(mapper_result, collections.abc.Iterable):
                result = Observable.from_(mapper_result)
            else:
                result = Observable.from_future(mapper_result) if is_future(
                    mapper_result) else mapper_result

            return result.mapi(lambda y, i: result_mapper_indexed(x, y, i))

        return source.flat_mapi(mapper_indexed=projection)

    if callable(mapper_indexed):
        ret = _flat_map(source, mapper_indexed=mapper_indexed)
    else:
        ret = _flat_map(source, mapper=lambda _: mapper_indexed)
    return ret
