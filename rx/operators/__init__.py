from typing import Callable, Union, Any
from datetime import timedelta

from rx.core import Observable
from rx.core.typing import Mapper, MapperIndexed, Predicate, PredicateIndexed


def all(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=W0622
    """Determines whether all elements of an observable sequence satisfy a
    condition.

    Example:
        >>> op = all(lambda value: value.length > 3)

    Args:
        predicate -- A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
    """
    from rx.core.operators.all import all as all_
    return all_(predicate)


def average(key_mapper=None) -> Callable[[Observable], Observable]:
    """Computes the average of an observable sequence of values that are in
    the sequence or obtained by invoking a transform function on each
    element of the input sequence if present.

    Examples:
        >>> op = average()
        >>> op = average(lambda x: x.value)

    Args:
        key_mapper -- A transform function to apply to each element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        average of the sequence of values.
    """
    from rx.core.operators.average import average as average_
    return average_(key_mapper)


def count(predicate=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence containing a value that represents
    how many elements in the specified observable sequence satisfy a
    condition if provided, else the count of items.

    Examples:
        >>> op = count()
        >>> op = count(lambda x: x > 3)

    Args:
        predicate -- A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with a number
        that represents how many elements in the input sequence satisfy
        the condition in the predicate function if provided, else
        the count of items in the sequence.
    """

    from rx.core.operators.count import count as count_
    return count_(predicate)


def filter(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> filter(lambda value: value < 10)(source)

    Args:
        predicate --  A function to test each source element for a
            condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence that contains elements from the input
        sequence that satisfy the condition.
    """
    from rx.core.operators.filter import filter as filter_
    return filter_(predicate)


def filteri(predicate_indexed: PredicateIndexed = None) -> Callable[[Observable], Observable]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> filter(lambda value, index: (value + index) < 10)(source)

    Args:
        predicate -- A function to test each source element for a
            condition; the second parameter of the function represents the
            index of the source element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence that contains elements from the input
        sequence that satisfy the condition.
    """
    from rx.core.operators.filter import filteri as filteri_
    return filteri_(predicate_indexed)


def last(predicate: Predicate = None) -> Callable[[Observable], Observable]:
    """Returns the last element of an observable sequence that satisfies the
    condition in the predicate if specified, else the last element.

    Examples:
        >>> op = last()
        >>> op = last(lambda x: x > 3)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing the last element in the
        observable sequence that satisfies the condition in the
        predicate.
    """
    from rx.core.operators.last import last as last_
    return last_(predicate)


def map(mapper: Mapper = None) -> Callable[[Observable], Observable]:  # By design. pylint: disable=W0622
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> map(lambda value: value * 10)

    Keyword arguments:
    mapper -- A transform function to apply to each source element; the
        second parameter of the function represents the index of the
        source element

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """
    from rx.core.operators.map import map as map_
    return map_(mapper)


def mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> ret = map(lambda value, index: value * value + index)(source)

    Args:
        mapper_indexed -- A transform function to apply to each source
            element; the second parameter of the function represents the
            index of the source element.

    Return:
        A operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """
    from rx.core.operators.map import mapi as mapi_
    return mapi_(mapper_indexed)


def delay(duetime: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    """Time shifts the observable sequence by duetime. The relative time
    intervals between the values are preserved.

    Examples:
        >>> op = delay(timedelta(seconds=10))
        >>> op = delay(5000)

    Args:
        duetime -- Relative time specified as an integer denoting
        milliseconds or datetime.timedelta by which to shift the
        observable sequence.

    Returns:
        An operator function that takes a source observable and returns
        a time-shifted sequence.
    """
    from rx.core.operators.delay import delay as delay_
    return delay_(duetime)


def flat_map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    Example:
        >>> source.flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences into
    one observable sequence.

    Example:
        >>> source.flat_map(Observable.of(1, 2, 3))

    Keyword arguments:
    mapper -- A transform function to apply to each element or an
        observable sequence to project each element from the source
        sequence onto.

    Returns:
        An operator function that takes a source observable and returns
        an observable sequence whose elements are the result of invoking
        the one-to-many transform function on each element of the
        input sequence .
    """
    from rx.core.operators.flatmap import flat_map as flat_map_
    return flat_map_(mapper)


def flat_mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    1 - source.flat_mapi(lambda x, i: Observable.range(0, x))

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

    Returns an observable sequence whose elements are the result of
    invoking the one-to-many transform function on each element of the
    input sequence.
    """
    from rx.core.operators.flatmap import flat_mapi as flat_mapi_
    return flat_mapi_(mapper_indexed)


def reduce(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Observable:
    """Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results, see
    Observable.scan.

    Examples:
        >>> res = reduce(lambda acc, x: acc + x)
        >>> res = reduce(lambda acc, x: acc + x, 0)

    Keyword arguments:
        accumulator -- An accumulator function to be
            invoked on each element.
        seed -- Optional initial accumulator value.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        final accumulator value.
    """
    from rx.core.operators.reduce import reduce as reduce_
    return reduce_(accumulator, seed)
