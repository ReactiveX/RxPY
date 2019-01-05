from typing import Callable, Union, Any
from datetime import timedelta

from rx.core import Observable, typing
from rx.core.typing import Mapper, MapperIndexed, Predicate, PredicateIndexed


def all(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=redefined-builtin
    """Determines whether all elements of an observable sequence satisfy
    a condition.

    Example:
        >>> op = all(lambda value: value.length > 3)

    Args:
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
    """
    from rx.core.operators.all import all as all_
    return all_(predicate)


def average(key_mapper: Callable[[Any], Any] = None) -> Callable[[Observable], Observable]:
    """Computes the average of an observable sequence of values that are
    in the sequence or obtained by invoking a transform function on each
    element of the input sequence if present.

    Examples:
        >>> op = average()
        >>> op = average(lambda x: x.value)

    Args:
        key_mapper: A transform function to apply to each element.

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
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with a number
        that represents how many elements in the input sequence satisfy
        the condition in the predicate function if provided, else
        the count of items in the sequence.
    """

    from rx.core.operators.count import _count
    return _count(predicate)


def debounce(duetime: Union[int, timedelta]) -> Callable[[Observable], Observable]:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    Example:
        >>> res = debounce(5000)(source) # 5 seconds

    Args:
        duetime: Duration of the throttle period for each value
        (specified as an integer denoting milliseconds).

    Returns:
        An operator function that takes the source observable and
        returns the debounced observable sequence.
    """
    from rx.core.operators.debounce import _debounce
    return _debounce(duetime)


throttle_with_timeout = debounce


def delay(duetime: Union[timedelta, int], scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    """The delay operator.

    Time shifts the observable sequence by duetime. The relative time
    intervals between the values are preserved.

    Examples:
        >>> res = delay(timedelta(seconds=10))
        >>> res = delay(5000)

    Args:
        duetime: Relative time specified as an integer denoting
            milliseconds or datetime.timedelta by which to shift the
            observable sequence.
        scheduler: [Optional] Scheduler to run the delay timers on.
            If not specified, the timeout scheduler is used.

    Returns:
        A partially applied operator function that takes the source
        observable and returns a time-shifted sequence.
    """
    from rx.core.operators.delay import _delay
    return _delay(duetime)


def distinct_until_changed(key_mapper=None, comparer=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence that contains only distinct
    contiguous elements according to the key_mapper and the comparer.

    Examples:
        >>> op = distinct_until_changed();
        >>> op = distinct_until_changed(lambda x: x.id)
        >>> op = distinct_until_changed(lambda x: x.id, lambda x, y: x == y)

    Args:
        key_mapper: [Optional] A function to compute the comparison key
            for each element. If not provided, it projects the value.
        comparer: [Optional] Equality comparer for computed key values.
            If not provided, defaults to an equality comparer function.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence only containing the distinct contiguous
        elements, based on a computed key value, from the source
        sequence.
    """
    from rx.core.operators.distinctuntilchanged import distinct_until_changed as distinct_until_changed_
    return distinct_until_changed_(key_mapper, comparer)


def do(observer: typing.Observer) -> Callable[[Observable], Observable]:
    """Invokes an action for each element in the observable sequence and
    invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging, logging,
    etc. of query behavior by intercepting the message stream to run
    arbitrary actions for messages on the pipeline.

    >>> do(observer)

    Args:
        observer: Observer

    Returns:
        An operator function that takes the source observable and
        returns the source sequence with the side-effecting behavior
        applied.
    """
    from rx.core.operators.do import do as do_
    return do_(observer)


def do_action(on_next: typing.OnNext = None,
              on_error: typing.OnError = None,
              on_completed: typing.OnCompleted = None
              ) -> Callable[[Observable], Observable]:
    """Invokes an action for each element in the observable sequence and
    invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging, logging,
    etc. of query behavior by intercepting the message stream to run
    arbitrary actions for messages on the pipeline.

    Examples:
        >>> do_action(send)(observable)
        >>> do_action(on_next, on_error)(observable)
        >>> do_action(on_next, on_error, on_completed)(observable)

    Args:
        on_next: [Optional] Action to invoke for each element in the
            observable sequence.
        on_error: [Optional] Action to invoke on exceptional
            termination of the observable sequence.
        on_completed: [Optional] Action to invoke on graceful
            termination of the observable sequence.

    Returns:
        An operator function that takes the source observable an returns
        the source sequence with the side-effecting behavior applied.
    """
    from rx.core.operators.do import do_action as do_action_
    return do_action_(on_next, on_error, on_completed)


def filter(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=redefined-builtin
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> op = filter(lambda value: value < 10)

    Args:
        predicate: A function to test each source element for a
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
        >>> op = filter(lambda value, index: (value + index) < 10)(source)

    Args:
        predicate: A function to test each source element for a
            condition; the second parameter of the function represents
            the index of the source element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence that contains elements from the input
        sequence that satisfy the condition.
    """
    from rx.core.operators.filter import filteri as filteri_
    return filteri_(predicate_indexed)


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

    Args:
        mapper_indexed: [Optional] A transform function to apply to each
            element or an observable sequence to project each element
            from the source sequence onto.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the one-to-many transform function on each element of the input
        sequence.
    """
    from rx.core.operators.flatmap import flat_mapi as flat_mapi_
    return flat_mapi_(mapper_indexed)


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
    from rx.core.operators.flatmap import flat_map_latest as flat_map_latest_
    return flat_map_latest_(mapper)


def last(predicate: Predicate = None) -> Callable[[Observable], Observable]:
    """Returns the last element of an observable sequence that satisfies the
    condition in the predicate if specified, else the last element.

    Examples:
        >>> op = last()
        >>> op = last(lambda x: x > 3)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing the last element in the
        observable sequence that satisfies the condition in the
        predicate.
    """
    from rx.core.operators.last import last as last_
    return last_(predicate)

def last_or_default(predicate=None, default_value=None) -> Observable:
    """Return last or default element.

    Returns the last element of an observable sequence that satisfies
    the condition in the predicate, or a default value if no such
    element exists.

    Examples:
        >>> res = last_or_default()
        >>> res = last_or_default(lambda x: x > 3)
        >>> res = last_or_default(lambda x: x > 3, 0)
        >>> res = last_or_default(None, 0)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value: [Optional] The default value if no such element
            exists. If not specified, defaults to None.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing the last element in the
        observable sequence that satisfies the condition in the predicate,
        or a default value if no such element exists.
    """
    from rx.core.operators.lastordefault import _last_or_default
    return  _last_or_default(predicate, default_value)


def map(mapper: Mapper = None) -> Callable[[Observable], Observable]:  # pylint: disable=redefined-builtin
    """The map operator.

    Project each element of an observable sequence into a new form.

    Example:
        >>> map(lambda value: value * 10)

    Args:
        mapper: A transform function to apply to each source element.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence whose elements are
        the result of invoking the transform function on each element
        of the source.
    """
    from rx.core.operators.map import _map
    return _map(mapper)


def mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> ret = mapi(lambda value, index: value * value + index)

    Args:
        mapper_indexed: A transform function to apply to each source
            element. The second parameter of the function represents
            the index of the source element.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence whose elements are
        the result of invoking the transform function on each element
        of the source.
    """
    from rx.core.operators.map import _mapi
    return _mapi(mapper_indexed)


def materialize() -> Callable[[Observable], Observable]:
    """Materializes the implicit notifications of an observable
    sequence as explicit notification values.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the materialized
        notification values from the source sequence.
    """
    from rx.core.operators.materialize import materialize as materialize_
    return materialize_()


def max(comparer: Callable[[Any], bool] = None) -> Callable[[Observable], Observable]:  # pylint: disable=redefined-builtin
    """Returns the maximum value in an observable sequence according to
    the specified comparer.

    Examples:
        >>> op = max()
        >>> op = max(lambda x, y:  x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence containing a single
        element with the maximum element in the source sequence.
    """
    from rx.core.operators.max import _max
    return _max(comparer)

def max_by(key_mapper, comparer=None) -> Callable[[Observable], Observable]:
    """The max_by operator.

    Returns the elements in an observable sequence with the maximum
    key value according to the specified comparer.

    Examples:
        >>> res = max_by(lambda x: x.value)
        >>> res = max_by(lambda x: x.value, lambda x, y: x - y)

    Args:
        key_mapper: Key mapper function.
        comparer: [Optional] Comparer used to compare key values.

    Returns:
        A partially applied operator function that takes an observable
        source and return an observable sequence containing a list of
        zero or more elements that have a maximum key value.
    """
    from rx.core.operators.maxby import _max_by
    return _max_by(comparer)

def merge_all() -> Callable[[Observable], Observable]:
    """The merge_all operator.

    Merges an observable sequence of observable sequences into an
    observable sequence.

    Returns:
        A partially applied operator function that takes an observable
        source and returns the observable sequence that merges the
        elements of the inner sequences.
    """
    from rx.core.operators.merge import _merge_all
    return _merge_all()

def reduce(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Callable[[Observable], Observable]:
    """The reduce operator.

    Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results,
    see `scan`.

    Examples:
        >>> res = reduce(lambda acc, x: acc + x)
        >>> res = reduce(lambda acc, x: acc + x, 0)

    Args:
        accumulator -- An accumulator function to be invoked on each
            element.
        seed -- Optional initial accumulator value.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence containing a single
        element with the final accumulator value.
    """
    from rx.core.operators.reduce import _reduce
    return _reduce(accumulator, seed)


def scan(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Callable[[Observable], Observable]:
    """The scan operator.

    Applies an accumulator function over an observable sequence and
    returns each intermediate result. The optional seed value is used
    as the initial accumulator value. For aggregation behavior with no
    intermediate results, see `aggregate()` or `Observable()`.

    Examples:
        >>> scanned = source.scan(lambda acc, x: acc + x)
        >>> scanned = source.scan(lambda acc, x: acc + x, 0)

    Args:
        accumulator: An accumulator function to be invoked on each
            element.
        seed: [Optional] The initial accumulator value.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence containing the
        accumulated values.
    """
    from rx.core.operators.scan import _scan
    return _scan(accumulator, seed)


def start_with(*args: Any) -> Callable[[Observable], Observable]:
    """Prepends a sequence of values to an observable sequence.

    Example:
        >>> start_with(1, 2, 3)

    Returns:
        An operator function that takes a source observable and returns
        the source sequence prepended with the specified values.
    """
    from rx.core.operators.startswith import _start_with
    return _start_with(*args)


def switch_latest() -> Callable[[Observable], Observable]:
    """Transforms an observable sequence of observable sequences into an
    observable sequence producing values only from the most recent
    observable sequence.

    Returns:
        A partially applied operator function that takes an observable
        source and returns the observable sequence that at any point in
        time produces the elements of the most recent inner observable
        sequence that has been received.
    """
    from rx.core.operators.switchlatest import switch_latest as switch_latest_
    return switch_latest_()


def throttle_with_mapper(throttle_duration_mapper: Callable[[Any], Observable]) -> Callable[[Observable], Observable]:
    """The throttle_with_mapper operator.

    Ignores values from an observable sequence which are followed by
    another value within a computed throttle duration.

    Example:
        >>> op = throttle_with_mapper(lambda x: rx.Scheduler.timer(x+x))

    Args:
        throttle_duration_mapper: Mapper function to retrieve an
        observable sequence indicating the throttle duration for each
        given element.

    Returns:
        A partially applied operator function that takes an observable
        source and returns the throttled observable sequence.
    """
    from rx.core.operators.debounce import _throttle_with_mapper
    return _throttle_with_mapper(throttle_duration_mapper)


def timestamp() -> Callable[[Observable], Observable]:
    """The timestamp operator.

    Records the timestamp for each value in an observable sequence.

    Examples:
        >>> timestamp()

    Produces objects with attributes `value` and `timestamp`, where
    value is the original value.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence with timestamp
        information on values.
    """
    from rx.core.operators.timestamp import _timestamp
    return _timestamp()
