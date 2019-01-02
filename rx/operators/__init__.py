from typing import Callable, Union, Any
from datetime import timedelta

from rx.core import Observable
from rx.core.typing import Mapper, MapperIndexed

def count(predicate=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence containing a value that represents
    how many elements in the specified observable sequence satisfy a
    condition if provided, else the count of items.

    Examples:
        >>> res = count()(source)
        >>> res = count(lambda x: x > 3)(source)

    Args:
        predicate -- A function to test each element for a condition.

    Returns an observable sequence containing a single element with a
    number that represents how many elements in the input sequence
    satisfy the condition in the predicate function if provided, else
    the count of items in the sequence.
    """
    from rx.core.operators.count import count as count_
    return count_(predicate)

def map(mapper: Mapper = None) -> Callable[[Observable], Observable]: # By design. pylint: disable=W0622
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> map(lambda value: value * 10)(source)

    Keyword arguments:
    mapper -- A transform function to apply to each source element; the
        second parameter of the function represents the index of the
        source element

    Returns:
        A function that takes an observable source and returns an
        observable sequence whose elements are the result of invoking
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
        mapper -- A transform function to apply to each source
            element; the second parameter of the function represents the
            index of the source element.

    Return:
        A function that takes an observable source and returns an
        observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """
    from rx.core.operators.map import mapi as mapi_
    return mapi_(mapper_indexed)

def delay(duetime: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    """Time shifts the observable sequence by duetime. The relative time
    intervals between the values are preserved.

    Examples:
        >>> res = delay(timedelta(seconds=10))
        >>> res = delay(5000)

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
