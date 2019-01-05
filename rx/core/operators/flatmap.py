import collections
from typing import Callable

from rx import from_, from_future, operators as _
from rx.core import Observable
from rx.core.typing import Mapper, MapperIndexed
from rx.internal.utils import is_future


def _flat_map(source, mapper=None, mapper_indexed=None):
    def projection(x, i):
        mapper_result = mapper(x) if mapper else mapper_indexed(x, i)
        if isinstance(mapper_result, collections.abc.Iterable):
            result = from_(mapper_result)
        else:
            result = from_future(mapper_result) if is_future(
                mapper_result) else mapper_result
        return result

    return source.pipe(
        _.mapi(projection),
        _.merge_all()
    )


def flat_map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    Example:
        >>> flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences
    into one observable sequence.

    Example:
        >>> flat_map(Observable.of(1, 2, 3))

    Args:
        mapper: A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.

    Returns:
        An operator function that takes a source observable and returns
        an observable sequence whose elements are the result of invoking
        the one-to-many transform function on each element of the
        input sequence .
    """

    def partial(source: Observable) -> Observable:
        if callable(mapper):
            ret = _flat_map(source, mapper=mapper)
        else:
            ret = _flat_map(source, mapper=lambda _: mapper)

        return ret
    return partial


def flat_mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

        >>> flat_mapi(lambda x, i: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences
    into one observable sequence.

        >>> flat_mapi(Observable.of(1, 2, 3))

    Args:
        mapper_indexed: [Optional] A transform function to apply to
            each element or an observable sequence to project each
            element from the source sequence onto.

    Returns:
        An operator function that takes a source observable and returns
        an observable sequence whose elements are the result of invoking
        the one-to-many transform function on each element of the input
        sequence.
    """

    def partial(source: Observable) -> Observable:
        if callable(mapper_indexed):
            ret = _flat_map(source, mapper_indexed=mapper_indexed)
        else:
            ret = _flat_map(source, mapper=lambda _: mapper_indexed)
        return ret
    return partial


def flat_map_latest(mapper: Mapper) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into a new
    sequence of observable sequences by incorporating the element's
    index and then transforms an observable sequence of observable
    sequences into an observable sequence producing values only from
    the most recent observable sequence.

    Args:
        mapper: A transform function to apply to each source element.
            The second parameter of the function represents the index of
            the source element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the transform function on each element of source producing an
        observable of Observable sequences and that at any point in time
        produces the elements of the most recent inner observable
        sequence that has been received.
    """
    def partial(source: Observable) -> Observable:
        return source.pipe(
            _.map(mapper),
            _.switch_latest()
        )
    return partial
