# pylint: disable=too-many-lines,redefined-outer-name,redefined-builtin

from asyncio import Future
from typing import Callable, Union, Any, Iterable, List
from datetime import timedelta, datetime

from rx.core import Observable, ConnectableObservable, GroupedObservable, BlockingObservable, typing
from rx.core.typing import Mapper, MapperIndexed, Predicate, PredicateIndexed
from rx.subjects import Subject


def all(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Determines whether all elements of an observable sequence satisfy
    a condition.

    Example:
        >>> op = all(lambda value: value.length > 3)

    Args:
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element
        determining whether all elements in the source sequence pass
        the test in the specified predicate.
    """
    from rx.core.operators.all import _all
    return _all(predicate)


def amb(right_source: Observable) -> Callable[[Observable], Observable]:
    """Propagates the observable sequence that reacts first.

    Example:
        >>> op = amb(ys)

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that surfaces any of the given
        sequences, whichever reacted first.
    """
    from rx.core.operators.amb import _amb
    return _amb(right_source)


def as_observable() -> Callable[[Observable], Observable]:
    """Hides the identity of an observable sequence.

    Returns:
        An operator function that takes an observable source and
        returns and observable sequence that hides the identity of the
        source sequence.
    """
    from rx.core.operators.asobservable import _as_observable
    return _as_observable()


def average(key_mapper: Callable[[Any], Any] = None) -> Callable[[Observable], Observable]:
    """The average operator.

    Computes the average of an observable sequence of values that
    are in the sequence or obtained by invoking a transform function on
    each element of the input sequence if present.

    Examples:
        >>> op = average()
        >>> op = average(lambda x: x.value)

    Args:
        key_mapper: A transform function to apply to each element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element with
        the average of the sequence of values.
    """
    from rx.core.operators.average import _average
    return _average(key_mapper)


def buffer(buffer_openings=None, buffer_closing_mapper=None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more buffers.

    Args:
        buffer_openings: Observable sequence whose elements denote the
            creation of windows.
        buffer_closing_mapper: [optional] A function invoked to define
            the closing of each produced window. If a closing mapper
            function is specified for the first parameter, this
            parameter is ignored.

    Returns:
        A function that takes an observable source and retuerns an
        observable sequence of windows.
    """
    from rx.core.operators.buffer import _buffer
    return _buffer(buffer_openings, buffer_closing_mapper)


def buffer_with_count(count: int, skip: int = None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    Examples:
        >>> res = buffer_with_count(10)(xs)
        >>> res = buffer_with_count(10, 1)(xs)

    Args:
        count: Length of each buffer.
        skip: [Optional] Number of elements to skip between
            creation of consecutive buffers. If not provided, defaults to
            the count.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """
    from rx.core.operators.buffer import _buffer_with_count
    return _buffer_with_count(count, skip)


def buffer_with_time(timespan, timeshift=None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on timing information.

    Examples:
        # non-overlapping segments of 1 second
        >>> res = buffer_with_time(1000)
        # segments of 1 second with time shift 0.5 seconds
        >>> res = buffer_with_time(1000, 500)

    Args:
        timespan: Length of each buffer (specified as an integer denoting
            milliseconds).
        timeshift: [Optional] Interval between creation of consecutive
            buffers (specified as an integer denoting milliseconds), or an
            optional scheduler parameter. If not specified, the time shift
            corresponds to the timespan parameter, resulting in non-overlapping
            adjacent buffers.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of buffers.
    """
    from rx.core.operators.bufferwithtime import _buffer_with_time
    return _buffer_with_time(timespan, timeshift)


def buffer_with_time_or_count(timespan, count, scheduler=None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into a buffer
    that is completed when either it's full or a given amount of time
    has elapsed.

    Examples:
        # 5s or 50 items in an array
        >>> res = source.buffer_with_time_or_count(5000, 50)
        # 5s or 50 items in an array
        >>> res = source.buffer_with_time_or_count(5000, 50, Scheduler.timeout)

    Args:
        timespan: Maximum time length of a buffer.
        count: Maximum element count of a buffer.
        scheduler: [Optional] Scheduler to run bufferin timers on. If not
            specified, the timeout scheduler is used.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of buffers.
    """
    from rx.core.operators.bufferwithtimeorcount import _buffer_with_time_or_count
    return _buffer_with_time_or_count(timespan, count, scheduler)


def catch_exception(second: Observable = None, handler=None) -> Callable[[Observable], Observable]:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> catch_exception(ys)(xs)
        >>> catch_exception(lambda ex: ys(ex))(xs)

    Args:
        handler: Exception handler function that returns an observable
            sequence given the error that occurred in the first
            sequence.
        second: Second observable sequence used to produce results
            when an error occurred in the first sequence.

    Returns:
        A function taking an observable source and returns an
        observable sequence containing the first sequence's elements,
        followed by the elements of the handler sequence in case an
        exception occurred.
    """
    from rx.core.operators.catch import _catch_exception
    return _catch_exception(second, handler)


def combine_latest(other: Union[Observable, Iterable[Observable]], mapper: Callable[[Any], Any]
                  ) -> Callable[[Observable], Observable]:
    """Merges the specified observable sequences into one observable
    sequence by using the mapper function whenever any of the
    observable sequences produces an element.

    Examples:
        >>> obs = combine_latest(other, lambda o1, o2, o3: o1 + o2 + o3)
        >>> obs = combine_latest([obs1, obs2, obs3], lambda o1, o2, o3: o1 + o2 + o3)

    Returns:
        An operator function that takes an observable sources and
        returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
    """
    from rx.core.operators.combinelatest import _combine_latest
    return _combine_latest(other, mapper)


def concat(*args: Union[Observable, Iterable[Observable]]) -> Callable[[Observable], Observable]:
    """Concatenates all the observable sequences.

    Examples:
        >>> res = concat(xs, ys, zs)
        >>> res = concat([xs, ys, zs])

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements of
        each given sequence, in sequential order.
    """
    from rx.core.operators.concat import _concat
    return _concat(*args)


def contains(value: Any, comparer=None) -> Callable[[Observable], Observable]:
    """Determines whether an observable sequence contains a specified
    element with an optional equality comparer.

    Examples:
        >>> res = contains(42)
        >>> res = contains({ "value": 42 }, lambda x, y: x["value"] == y["value")

    Args:
        value: The value to locate in the source sequence.
        comparer: [Optional] An equality comparer to compare elements.

    Returns:
        A function that takes a source observable that returns an
        observable  sequence containing a single element determining
        whether the source sequence contains an element that has the
        specified value.
    """
    from rx.core.operators.contains import _contains
    return _contains(value, comparer)


def count(predicate=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence containing a value that
    represents how many elements in the specified observable sequence
    satisfy a condition if provided, else the count of items.

    Examples:
        >>> op = count()
        >>> op = count(lambda x: x > 3)

    Args:
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element with
        a number that represents how many elements in the input
        sequence satisfy the condition in the predicate function if
        provided, else the count of items in the sequence.
    """

    from rx.core.operators.count import _count
    return _count(predicate)


def debounce(duetime: Union[int, timedelta], scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    Example:
        >>> res = debounce(5000) # 5 seconds

    Args:
        duetime: Duration of the throttle period for each value
            (specified as an integer denoting milliseconds).
        scheduler: Scheduler to debounce values on.

    Returns:
        An operator function that takes the source observable and
        returns the debounced observable sequence.
    """
    from rx.core.operators.debounce import _debounce
    return _debounce(duetime, scheduler)


throttle_with_timeout = debounce


def default_if_empty(default_value: Any = None) -> Callable[[Observable], Observable]:
    """Returns the elements of the specified sequence or the specified
    value in a singleton sequence if the sequence is empty.

    Examples:
        >>> res = obs = default_if_empty()
        >>> obs = default_if_empty(False)

    Args:
        default_value: The value to return if the sequence is empty. If
            not provided, this defaults to None.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the specified
        default value if the source is empty otherwise, the elements of
        the source.
    """
    from rx.core.operators.defaultifempty import _default_if_empty
    return _default_if_empty(default_value)


def delay_subscription(duetime: Union[datetime, int]) -> Callable[[Observable], Observable]:
    """Time shifts the observable sequence by delaying the
    subscription.

    Example:
        >>> res = delay_subscription(5000) # 5s

    Args:
        duetime: Absolute or relative time to perform the subscription
        at.

    Returns:
        A function that take a source observable and returns a
        time-shifted observable sequence.
    """
    from rx.core.operators.delaysubscription import _delay_subscription
    return _delay_subscription(duetime)


def delay_with_mapper(subscription_delay=None, delay_duration_mapper=None) -> Callable[[Observable], Observable]:
    """Time shifts the observable sequence based on a subscription delay
    and a delay mapper function for each element.

    Examples:
        # with mapper only
        >>> res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
        # with delay and mapper
        >>> res = source.delay_with_selector(Observable.timer(2000),
                                            lambda x: Observable.timer(x))

    Args:
        subscription_delay: [Optional] Sequence indicating the delay for the
            subscription to the source.
        delay_duration_mapper: [Optional] Selector function to retrieve a
            sequence indicating the delay for each given element.

    Returns:
        A function that takes an observable source and retursn a
        time-shifted observable sequence.
    """
    from rx.core.operators.delaywithmapper import _delay_with_mapper
    return _delay_with_mapper(subscription_delay, delay_duration_mapper)


def dematerialize() -> Callable[[Observable], Observable]:
    """Dematerialize operator.

    Dematerializes the explicit notification values of an
    observable sequence as implicit notifications.

    Returns:
        An observable sequence exhibiting the behavior
        corresponding to the source sequence's notification values.
    """
    from rx.core.operators.dematerialize import _dematerialize
    return _dematerialize()


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


def distinct(key_mapper=None, comparer=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence that contains only distinct
    elements according to the key_mapper and the comparer. Usage of
    this operator should be considered carefully due to the maintenance
    of an internal lookup structure which can grow large.

    Examples:
        >>> res = obs = xs.distinct()
        >>> obs = xs.distinct(lambda x: x.id)
        >>> obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)

    Args:
        key_mapper: [Optional]  A function to compute the comparison key
            for each element.
        comparer: [Optional]  Used to compare items in the collection.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence only containing the distinct
        elements, based on a computed key value, from the source
        sequence.
    """
    from rx.core.operators.distinct import _distinct
    return _distinct(key_mapper, comparer)


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
        An operator function that takes an observable source and
        returns an observable sequence only containing the distinct
        contiguous elements, based on a computed key value, from the
        source sequence.
    """
    from rx.core.operators.distinctuntilchanged import distinct_until_changed as distinct_until_changed_
    return distinct_until_changed_(key_mapper, comparer)


def do(observer: typing.Observer) -> Callable[[Observable], Observable]:
    """Invokes an action for each element in the observable sequence
    and invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging,
    logging, etc. of query behavior by intercepting the message stream
    to run arbitrary actions for messages on the pipeline.

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


def do_action(on_next: typing.OnNext = None, on_error: typing.OnError = None, on_completed: typing.OnCompleted = None
              ) -> Callable[[Observable], Observable]:
    """Invokes an action for each element in the observable sequence
    and invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging,
    logging, etc. of query behavior by intercepting the message stream
    to run arbitrary actions for messages on the pipeline.

    Examples:
        >>> do_action(send)
        >>> do_action(on_next, on_error)
        >>> do_action(on_next, on_error, on_completed)

    Args:
        on_next: [Optional] Action to invoke for each element in the
            observable sequence.
        on_error: [Optional] Action to invoke on exceptional
            termination of the observable sequence.
        on_completed: [Optional] Action to invoke on graceful
            termination of the observable sequence.

    Returns:
        An operator function that takes the source observable an
        returns the source sequence with the side-effecting behavior
        applied.
    """
    from rx.core.operators.do import do_action as do_action_
    return do_action_(on_next, on_error, on_completed)


def do_while(condition: Callable[[Any], bool]) -> Callable[[Observable], Observable]:
    """Repeats source as long as condition holds emulating a do while
    loop.

    Args:
        condition: The condition which determines if the source will be
            repeated.

    Returns:
        An observable sequence which is repeated as long
        as the condition holds.
    """
    from rx.core.operators.dowhile import _do_while
    return _do_while(condition)


def element_at(index: int) -> Callable[[Observable], Observable]:
    """Returns the element at a specified index in a sequence.

    Example:
        >>> res = source.element_at(5)

    Args:
        index: The zero-based index of the element to retrieve.

    Returns:
        An operator function that takes an observable source and
        returns an observable  sequence that produces the element at
        the specified position in the source sequence.
    """
    from rx.core.operators.elementatordefault import _element_at_or_default
    return _element_at_or_default(index, False)


def element_at_or_default(index: int, default_value: Any = None) -> Callable[[Observable], Observable]:
    """Returns the element at a specified index in a sequence or a
    default value if the index is out of range.

    Example:
        >>> res = source.element_at_or_default(5)
        >>> res = source.element_at_or_default(5, 0)

    Args:
        index -- The zero-based index of the element to retrieve.
        default_value -- [Optional] The default value if the index is
            outside the bounds of the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence that produces the element at the
        specified position in the source sequence, or a default value if
        the index is outside the bounds of the source sequence.
    """
    from rx.core.operators.elementatordefault import _element_at_or_default
    return _element_at_or_default(index, True, default_value)


def expand(mapper: Mapper) -> Observable:
    """Expands an observable sequence by recursively invoking mapper.

    Args:
        mapper: Mapper function to invoke for each produced element,
            resulting in another sequence to which the mapper will be
            invoked recursively again.

    Returns:
        An observable sequence containing all the elements produced
    by the recursive expansion.
    """
    from rx.core.operators.expand import _expand
    return _expand(mapper)


def filter(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=redefined-builtin
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> op = filter(lambda value: value < 10)

    Args:
        predicate: A function to test each source element for a
        condition.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains elements from the
        input sequence that satisfy the condition.
    """
    from rx.core.operators.filter import _filter
    return _filter(predicate)


def filteri(predicate_indexed: PredicateIndexed = None) -> Callable[[Observable], Observable]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> op = filter(lambda value, index: (value + index) < 10)

    Args:
        predicate: A function to test each source element for a
            condition; the second parameter of the function represents
            the index of the source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains elements from the
        input sequence that satisfy the condition.
    """
    from rx.core.operators.filter import _filteri
    return _filteri(predicate_indexed)


def finally_action(action: Callable) -> Callable[[Observable], Observable]:
    """Invokes a specified action after the source observable sequence
    terminates gracefully or exceptionally.

    Example:
        res = finally(lambda: print('sequence ended')

    Args:
        action: Action to invoke after the source observable sequence
            terminates.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the action-invoking
        termination behavior applied.
    """
    from rx.core.operators.finallyaction import _finally_action
    return _finally_action(action)


def find(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Searches for an element that matches the conditions defined by
    the specified predicate, and returns the first occurrence within
    the entire Observable sequence.

    Args:
        predicate: The predicate that defines the conditions of the
            element to search for.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the first element that
        matches the conditions defined by the specified predicate, if
        found otherwise, None.
    """
    from rx.core.operators.find import _find_value
    return _find_value(predicate, False)


def find_index(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Searches for an element that matches the conditions defined by
    the specified predicate, and returns an Observable sequence with the
    zero-based index of the first occurrence within the entire
    Observable sequence.

    Keyword Arguments:
    predicate -- The predicate that defines the conditions of the
        element to search for.

    Returns an observable sequence with the zero-based index of the
    first occurrence of an element that matches the conditions defined
    by match, if found; otherwise, -1.
    """
    from rx.core.operators.find import _find_value
    return _find_value(predicate, True)


def first(predicate=None) -> Callable[[Observable], Observable]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    Examples:
        >>> res = res = first()
        >>> res = res = first(lambda x: x > 3)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate if
        provided, else the first item in the sequence.
    """
    from rx.core.operators.first import _first
    return _first(predicate)


def first_or_default(predicate: Predicate = None, default_value: Any = None) -> Callable[[Observable], Observable]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate, or a default value if no
    such element exists.

    Examples:
        >>> res = first_or_default()
        >>> res = first_or_default(lambda x: x > 3)
        >>> res = first_or_default(lambda x: x > 3, 0)
        >>> res = first_or_default(None, 0)

    Args:
        predicate: [optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value: [Optional] The default value if no such element
            exists.  If not specified, defaults to None.

    Returns:
        A function that takes an observable source and reutrn an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
    """
    from rx.core.operators.firstordefault import _first_or_default
    return _first_or_default(predicate, default_value)


def flat_map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """The flat_map operator.

    One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    Example:
        >>> flat_map(lambda x: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the
    other observable sequence and merges the resulting observable
    sequences into one observable sequence.

    Example:
        >>> flat_map(Observable.of(1, 2, 3))

    Args:
        mapper: A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.

    Returns:
        An operator function that takes a source observable and returns
        an observable sequence whose elements are the result of
        invoking the one-to-many transform function on each element of
        the input sequence.
    """
    from rx.core.operators.flatmap import _flat_map
    return _flat_map(mapper)


def flat_mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """The `flat_mapi` operator.

    One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    Example:
        >>> source.flat_mapi(lambda x, i: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the other
    observable sequence and merges the resulting observable sequences
    into one observable sequence.

    Example:
        >>> source.flat_mapi(Observable.of(1, 2, 3))

    Args:
        mapper_indexed: [Optional] A transform function to apply to
            each element or an observable sequence to project each
            element from the source sequence onto.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function on each element of
        the input sequence.
    """
    from rx.core.operators.flatmap import _flat_mapi
    return _flat_mapi(mapper_indexed)


def flat_map_latest(mapper: Mapper) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into a new
    sequence of observable sequences by incorporating the element's
    index and then transforms an observable sequence of observable
    sequences into an observable sequence producing values only from
    the most recent observable sequence.

    Args:
        mapper: A transform function to apply to each source element.
            The second parameter of the function represents the index
            of the source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source
        producing an observable of Observable sequences and that at any
        point in time produces the elements of the most recent inner
        observable sequence that has been received.
    """
    from rx.core.operators.flatmap import _flat_map_latest
    return _flat_map_latest(mapper)


def group_by(key_mapper, element_mapper=None) -> Callable[[Observable], Observable]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function and comparer and selects the
    resulting elements by using a specified function.

    Examples:
        >>> group_by(lambda x: x.id)
        >>> group_by(lambda x: x.id, lambda x: x.name)
        >>> group_by(lambda x: x.id, lambda x: x.name, lambda x: str(x))

    Keyword arguments:
        key_mapper: A function to extract the key for each element.
        element_mapper: [Optional] A function to map each source
            element to an element in an observable group.

    Returns:
        An operator function that takes an observable source and
        returns a sequence of observable groups, each of which
        corresponds to a unique key value, containing all elements that
        share that same key value.
    """
    from rx.core.operators.groupby import _group_by
    return _group_by(key_mapper, element_mapper)


def group_by_until(key_mapper, element_mapper, duration_mapper) -> Callable[[Observable], Observable]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function. A duration mapper function is used
    to control the lifetime of groups. When a group expires, it
    receives an OnCompleted notification. When a new element with the
    same key value as a reclaimed group occurs, the group will be
    reborn with a new lifetime request.

    Examples:
        >>> group_by_until(lambda x: x.id, None, lambda : rx.never())
        >>> group_by_until(lambda x: x.id,lambda x: x.name, lambda: rx.never())
        >>> group_by_until(lambda x: x.id,lambda x: x.name, lambda: rx.never(), lambda x: str(x))

    Args:
        key_mapper: A function to extract the key for each element.
        duration_mapper: A function to signal the expiration of a group.

    Returns:
        An operator function that takes an observable source and
        returns a sequence of observable groups, each of which
        corresponds to a unique key value, containing all elements that
        share that same key value. If a group's lifetime expires, a new
        group with the same key value can be created once an element
        with such a key value is encountered.
    """
    from rx.core.operators.groupbyuntil import _group_by_until
    return _group_by_until(key_mapper, element_mapper, duration_mapper)


def group_join(right, left_duration_mapper, right_duration_mapper, result_mapper
               ) -> Callable[[Observable], Observable]:
    """Correlates the elements of two sequences based on overlapping
    durations, and groups the results.

    Args:
        right: The right observable sequence to join elements for.
        left_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the left observable sequence, used to determine overlap.
        right_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the right observable sequence, used to determine overlap.
        result_mapper: A function invoked to compute a result element
            for any element of the left sequence with overlapping
            elements from the right observable sequence. The first
            parameter passed to the function is an element of the left
            sequence. The second parameter passed to the function is an
            observable sequence with elements from the right sequence
            that overlap with the left sequence's element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains result elements
        computed from source elements that have an overlapping
        duration.
    """
    from rx.core.operators.groupjoin import _group_join
    return _group_join(right, left_duration_mapper, right_duration_mapper, result_mapper)


def ignore_elements() -> Observable:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns:
        An operator function that takes an observable source and
        returns an empty observable sequence that signals termination,
        successful or exceptional, of the source sequence.
    """
    from rx.core.operators.ignoreelements import _ignore_elements
    return _ignore_elements()


def is_empty() -> Callable[[Observable], Observable]:
    """Determines whether an observable sequence is empty.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element
        determining whether the source sequence is empty.
    """
    from rx.core.operators.isempty import _is_empty
    return _is_empty()


def join(right, left_duration_mapper, right_duration_mapper, result_mapper) -> Callable[[Observable], Observable]:
    """Correlates the elements of two sequences based on overlapping
    durations.

    Args:
        right: The right observable sequence to join elements for.
        left_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the left observable sequence, used to determine overlap.
        right_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the right observable sequence, used to determine overlap.
        result_mapper: A function invoked to compute a result element
            for any two overlapping elements of the left and right
            observable sequences. The parameters passed to the function
            correspond with the elements from the left and right source
            sequences for which overlap occurs.

    Return:
        An operator function that takes an observable source and
        returns an observable sequence that contains result elements
        computed from source elements that have an overlapping
        duration.
    """
    from rx.core.operators.join import _join
    return _join(right, left_duration_mapper, right_duration_mapper, result_mapper)


def last(predicate: Predicate = None) -> Callable[[Observable], Observable]:
    """The last operator.

    Returns the last element of an observable sequence that satisfies
    the condition in the predicate if specified, else the last element.

    Examples:
        >>> op = last()
        >>> op = last(lambda x: x > 3)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the last element in
        the observable sequence that satisfies the condition in the
        predicate.
    """
    from rx.core.operators.last import _last
    return _last(predicate)

def last_or_default(predicate=None, default_value=None) -> Observable:
    """The last_or_default operator.

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
        An operator function that takes an observable source and
        returns an observable sequence containing the last element in
        the observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
    """
    from rx.core.operators.lastordefault import _last_or_default
    return  _last_or_default(predicate, default_value)


def map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.materialize import _materialize
    return _materialize()


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
    return _max_by(key_mapper, comparer)


def merge(*args, max_concurrent: int = None) -> Callable[[Observable], Observable]:
    """Merges an observable sequence of observable sequences into an
    observable sequence, limiting the number of concurrent
    subscriptions to inner sequences. Or merges two observable
    sequences into a single observable sequence.

    Examples:
        >>> merged = merge(max_concurrent=1)
        >>> merged = merge(other_source)

    Args:
        max_concurrent: [Optional] Maximum number of inner observable
            sequences being subscribed to concurrently or the second
            observable sequence.

    Returns:
        An operator function that takes an observable source and
        returns the observable sequence that merges the elements of the
        inner sequences.
    """
    from rx.core.operators.merge import _merge
    return _merge(*args, max_concurrent=max_concurrent)


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


def min(comparer: Callable = None) -> Callable[[Observable], Observable]:
    """The `min` operator.

    Returns the minimum element in an observable sequence according to
    the optional comparer else a default greater than less than check.

    Examples:
        >>> res = source.min()
        >>> res = source.min(lambda x, y: x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An operator function that takes an observable source and
        reuturns an observable sequence containing a single element
        with the minimum element in the source sequence.
    """
    from rx.core.operators.min import _min
    return _min(comparer)


def min_by(key_mapper, comparer=None) -> Observable:
    """The `min_by` operator.

    Returns the elements in an observable sequence with the minimum key
    value according to the specified comparer.

    Examples:
        >>> res = min_by(lambda x: x.value)
        >>> res = min_by(lambda x: x.value, lambda x, y: x - y)

    Args:
        key_mapper: Key mapper function.
        comparer: [Optional] Comparer used to compare key values.

    Returns:
        An operator function that takes an observable source and
        reuturns an observable sequence containing a list of zero
        or more elements that have a minimum key value.
    """
    from rx.core.operators.minby import _min_by
    return _min_by(key_mapper, comparer)

def multicast(subject: Subject = None, subject_factory: Callable[[], Subject] = None,
              mapper: Mapper = None) -> Callable[[Observable], Union[Observable, ConnectableObservable]]:
    """Multicasts the source sequence notifications through an
    instantiated subject into all uses of the sequence within a mapper
    function. Each subscription to the resulting sequence causes a
    separate multicast invocation, exposing the sequence resulting from
    the mapper function's invocation. For specializations with fixed
    subject types, see Publish, PublishLast, and Replay.

    Examples:
        >>> res = multicast(observable)
        >>> res = multicast(subject_factory=lambda scheduler: Subject(), mapper=lambda x: x)

    Args:
        subject_factory: Factory function to create an intermediate
            subject through which the source sequence's elements will
            be multicast to the mapper function.
        subject: Subject to push source elements into.
        mapper: [Optional] Mapper function which can use the
            multicasted source sequence subject to the policies
            enforced by the created subject. Specified only if
            subject_factory" is a factory function.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from rx.core.operators.multicast import _multicast
    return _multicast(subject, subject_factory, mapper)


def observe_on(scheduler) -> Callable[[Observable], Observable]:
    """Wraps the source sequence in order to run its observer callbacks
    on the specified scheduler.

    Args:
        scheduler: Scheduler to notify observers on.

    This only invokes observer callbacks on a scheduler. In case the
    subscription and/or unsubscription actions have side-effects
    that require to be run on a scheduler, use subscribe_on.

    Returns:
        An operator function that takes an observable source and
        returns the source sequence whose observations happen on the
        specified scheduler.
    """
    from rx.core.operators.observeon import _observe_on
    return _observe_on(scheduler)

def on_error_resume_next(second) -> Callable[[Observable], Observable]:
    """Continues an observable sequence that is terminated normally
    or by an exception with the next observable sequence.

    Keyword arguments:
    second -- Second observable sequence used to produce results
        after the first sequence terminates.

    Returns an observable sequence that concatenates the first and
    second sequence, even if the first sequence terminates
    exceptionally.
    """

    from rx.core.operators.onerrorresumenext import _on_error_resume_next
    return _on_error_resume_next(second)


def pairwise() -> Callable[[Observable], Observable]:
    """The pairwise operator.

    Returns a new observable that triggers on the second and subsequent
    triggerings of the input observable. The Nth triggering of the
    input observable passes the arguments from the N-1th and Nth
    triggering as a pair. The argument passed to the N-1th triggering
    is held in hidden internal state until the Nth triggering occurs.

    Returns:
        An operator function that takes an observable source and
        returns an observable that triggers on successive pairs of
        observations from the input observable as an array.
    """
    from rx.core.operators.pairwise import _pairwise
    return _pairwise()


def partition(predicate: Predicate) -> Callable[[Observable], List[Observable]]:
    """Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations
    for those values for which the predicate returns true. The second
    will trigger observations for those values where the predicate
    returns false. The predicate is executed once for each subscribed
    observer. Both also propagate all error observations arising from
    the source and each completes when the source completes.

    Args:
        predicate: The function to determine which output Observable
        will trigger a particular observation.

    Returns:
        An operator function that takes an observable source and
        returns a list of observables. The first triggers when the
        predicate returns True, and the second triggers when the
        predicate returns False.
    """
    from rx.core.operators.partition import _partition
    return _partition(predicate)


def partitioni(predicate_indexed: PredicateIndexed) -> Callable[[Observable], List[Observable]]:
    """The indexed partition operator.

    Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations
    for those values for which the predicate returns true. The second
    will trigger observations for those values where the predicate
    returns false. The predicate is executed once for each subscribed
    observer. Both also propagate all error observations arising from
    the source and each completes when the source completes.

    Args:
        predicate: The function to determine which output Observable
        will trigger a particular observation.

    Returns:
        A list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate
        returns False.
    """
    from rx.core.operators.partition import _partitioni
    return _partitioni(predicate_indexed)


def pluck(key: Any) -> Callable[[Observable], Observable]:
    """Retrieves the value of a specified key using dict-like access (as in
    element[key]) from all elements in the Observable sequence.

    To pluck an attribute of each element, use pluck_attr.

    Args:
        key: The key to pluck.

    Returns:
        An operator function that takes an observable source and
        returns a new observable sequence of key values.
    """
    from rx.core.operators.pluck import _pluck
    return _pluck(key)


def pluck_attr(prop: str) -> Callable[[Observable], Observable]:
    """Retrieves the value of a specified property (using getattr) from
    all elements in the Observable sequence.

    To pluck values using dict-like access (as in element[key]) on each
    element, use pluck.

    Args:
        property: The property to pluck.

    Returns:
        An operator function that takes an observable source and
        returns a new observable sequence of property values.
    """
    from rx.core.operators.pluck import _pluck_attr
    return _pluck_attr(prop)


def publish(mapper=None) -> ConnectableObservable:
    """The `publish` operator.

    Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence. This operator is a
    specialization of Multicast using a regular Subject.

    Example:
        >>> res = publish()
        >>> res = publish(lambda x: x)

    Args:
        mapper: [Optional] Selector function which can use the
            multicasted source sequence as many times as needed,
            without causing multiple subscriptions to the source
            sequence. Subscribers to the given source will receive all
            notifications of the source from the time of the
            subscription on.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from rx.core.operators.publish import _publish
    return _publish(mapper)


def publish_value(initial_value: Any, mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence that is the result of invoking
    the mapper on a connectable observable sequence that shares a
    single subscription to the underlying sequence and starts with
    initial_value.

    This operator is a specialization of Multicast using a
    BehaviorSubject.

    Examples:
        >>> res = source.publish_value(42)
        >>> res = source.publish_value(42, lambda x: x.map(lambda y: y * y))

    Args:
        initial_value: Initial value received by observers upon
            subscription.
        mapper: [Optional] Optional mapper function which can use the
            multicasted source sequence as many times as needed,
            without causing multiple subscriptions to the source
            sequence. Subscribers to the given source will receive
            immediately receive the initial value, followed by all
            notifications of the source from the time of the
            subscription on.

    Returns:
        An operator function that takes an obserable source and returns
        an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from rx.core.operators.publishvalue import _publish_value
    return _publish_value(initial_value, mapper)


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
        accumulator: An accumulator function to be invoked on each
            element.
        seed: Optional initial accumulator value.

    Returns:
        A partially applied operator function that takes an observable
        source and returns an observable sequence containing a single
        element with the final accumulator value.
    """
    from rx.core.operators.reduce import _reduce
    return _reduce(accumulator, seed)


def ref_count() -> Callable[[ConnectableObservable], Observable]:
    """Returns an observable sequence that stays connected to the
    source as long as there is at least one subscription to the
    observable sequence.
    """
    from rx.core.operators.connectable.refcount import _ref_count
    return _ref_count()


def repeat(repeat_count=None) -> Callable[[Observable], Observable]:
    """Repeats the observable sequence a specified number of times.
    If the repeat count is not specified, the sequence repeats
    indefinitely.

    Examples:
        >>> repeated = repeat()
        >>> repeated = repeat(42)
    Args:
        repeat_count: Number of times to repeat the sequence. If not
        provided, repeats the sequence indefinitely.

    Returns:
        An operator function that takes an observable sources and
        returna an observable sequence producing the elements of the
        given sequence repeatedly.
    """
    from rx.core.operators.repeat import _repeat
    return _repeat(repeat_count)


def replay(mapper: Mapper = None, buffer_size: int = None, window: timedelta = None, scheduler: typing.Scheduler = None
          ) -> Callable[[Observable], Union[Observable, ConnectableObservable]]:
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence replaying notifications
    subject to a maximum time length for the replay buffer.

    This operator is a specialization of Multicast using a
    ReplaySubject.

    Examples:
        >>> res = replay(buffer_size=3)
        >>> res = replay(buffer_size=3, window=500)
        >>> res = replay(None, 3, 500)
        >>> res = replay(lambda x: x.take(6).repeat(), 3, 500)

    Args:
        mapper: [Optional] Selector function which can use the multicasted
            source sequence as many times as needed, without causing
            multiple subscriptions to the source sequence. Subscribers to
            the given source will receive all the notifications of the
            source subject to the specified replay buffer trimming policy.
        buffer_size: [Optional] Maximum element count of the replay
            buffer.
        window: [Optional] Maximum time length of the replay buffer.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from rx.core.operators.replay import _replay
    return _replay(mapper, buffer_size, window, scheduler)


def retry(retry_count: int = None) -> Callable[[Observable], Observable]:
    """Repeats the source observable sequence the specified number of
    times or until it successfully terminates. If the retry count is
    not specified, it retries indefinitely.

    Examples:
        >>> retried = retry()
        >>> retried = retry(42)

    Args:
        retry_count: [Optional] Number of times to retry the sequence.
            If not provided, retry the sequence indefinitely.

    Returns:
        An observable sequence producing the elements of the given
        sequence repeatedly until it terminates successfully.
    """
    from rx.core.operators.retry import _retry
    return _retry(retry_count)


def sample(interval=None, sampler=None) -> Callable[[Observable], Observable]:
    """Samples the observable sequence at each interval.

    Examples:
        >>> res = sample(sample_observable) # Sampler tick sequence
        >>> res = ample(5000) # 5 seconds

    Args:
        interval: Interval at which to sample (specified as an integer
            denoting milliseconds).

    Returns:
        An operator function that takes an observable source and
        returns a sampled observable sequence.
    """
    from rx.core.operators.sample import _sample
    return _sample(interval, sampler)


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


def sequence_equal(second: Observable, comparer: Callable[[Any, Any], bool] = None
                   ) -> Callable[[Observable], Observable]:
    """Determines whether two sequences are equal by comparing the
    elements pairwise using a specified equality comparer.

    Examples:
        >>> res = sequence_equal([1,2,3])
        >>> res = sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
        >>> res = sequence_equal(rx.return_value(42))
        >>> res = sequence_equal(rx.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

    Args:
        second: Second observable sequence or array to compare.
        comparer: [Optional] Comparer used to compare elements of both
            sequences. No guarantees on order of comparer arguments.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains a single element
        which indicates whether both sequences are of equal length and
        their corresponding elements are equal according to the
        specified equality comparer.
    """
    from rx.core.operators.sequenceequal import _sequence_equal
    return _sequence_equal(second, comparer)


def share() -> Callable[[Observable], Observable]:
    """Share a single subscription among multple observers.

    This is an alias for a composed publish() and ref_count().

    Returns:
        An operator function that takes an observable source and
        returns a new Observable that multicasts (shares) the original
        Observable. As long as there is at least one Subscriber this
        Observable will be subscribed and emitting data. When all
        subscribers have unsubscribed it will unsubscribe from the
        source
        Observable.
    """
    from rx.core.operators.publish import _share
    return _share()


def single(predicate: Predicate = None) -> Callable[[Observable], Observable]:
    """Returns the only element of an observable sequence that satisfies the
    condition in the optional predicate, and reports an exception if there
    is not exactly one element in the observable sequence.

    Example:
        >>> res = single()
        >>> res = single(lambda x: x == 42)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate.
    """
    from rx.core.operators.single import _single
    return _single(predicate)


def single_or_default(predicate: Predicate = None, default_value: Any = None) -> Observable:
    """Returns the only element of an observable sequence that matches
    the predicate, or a default value if no such element exists this
    method reports an exception if there is more than one element in the
    observable sequence.

    Examples:
        >>> res = single_or_default()
        >>> res = single_or_default(lambda x: x == 42)
        >>> res = single_or_default(lambda x: x == 42, 0)
        >>> res = single_or_default(None, 0)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value: [Optional] The default value if the index is
            outside the bounds of the source sequence.

    Returns:
        An observable Sequence containing the single element in the
    observable sequence that satisfies the condition in the predicate,
    or a default value if no such element exists.
    """
    from rx.core.operators.singleordefault import _single_or_default
    return _single_or_default(predicate, default_value)


def single_or_default_async(has_default: bool = False, default_value: Any = None):
    from rx.core.operators.singleordefault import _single_or_default_async
    return _single_or_default_async(has_default, default_value)


def skip(count: int) -> Callable[[Observable], Observable]:
    """The skip operator.

    Bypasses a specified number of elements in an observable sequence
    and then returns the remaining elements.

    Args:
        count: The number of elements to skip before returning the
            remaining elements.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements that
        occur after the specified index in the input sequence.
    """
    from rx.core.operators.skip import _skip
    return _skip(count)


def skip_last(count: int) -> Observable:
    """The skip_last operator.

    Bypasses a specified number of elements at the end of an observable
    sequence.

    This operator accumulates a queue with a length enough to store the
    first `count` elements. As more elements are received, elements are
    taken from the front of the queue and produced on the result
    sequence. This causes elements to be delayed.

    Args:
        count: Number of elements to bypass at the end of the source
        sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the source sequence
        elements except for the bypassed ones at the end.
    """
    from rx.core.operators.skiplast import _skip_last
    return _skip_last(count)


def skip_last_with_time(duration: Union[timedelta, int], scheduler: typing.Scheduler = None
                        ) -> Callable[[Observable], Observable]:
    """Skips elements for the specified duration from the end of the
    observable source sequence.

    Example:
        >>> res = skip_last_with_time(5000)

    This operator accumulates a queue with a length enough to store
    elements received during the initial duration window. As more
    elements are received, elements older than the specified duration
    are taken from the queue and produced on the result sequence. This
    causes elements to be delayed with duration.

    Args:
        duration: Duration for skipping elements from the end of the
            sequence.
        scheduler: Scheduler to use for time handling.

    Returns:
        An observable sequence with the elements skipped during the
    specified duration from the end of the source sequence.
    """
    from rx.core.operators.skiplastwithtime import _skip_last_with_time
    return _skip_last_with_time(duration, scheduler)


def skip_until(other: Observable) -> Callable[[Observable], Observable]:
    """Returns the values from the source observable sequence only
    after the other observable sequence produces a value.

    Args:
        other: The observable sequence that triggers propagation of
            elements of the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the elements of the
        source sequence starting from the point the other sequence
        triggered propagation.
    """
    from rx.core.operators.skipuntil import _skip_until
    return _skip_until(other)


def skip_until_with_time(start_time: Union[datetime, int]) -> Callable[[Observable], Observable]:
    """Skips elements from the observable source sequence until the
    specified start time.
    Errors produced by the source sequence are always forwarded to the
    result sequence, even if the error occurs before the start time.

    Examples:
        >>> res = source.skip_until_with_time(datetime);
        >>> res = source.skip_until_with_time(5000);

    Args:
        start_time -- Time to start taking elements from the source
            sequence. If this value is less than or equal to Date(), no
            elements will be skipped.

    Returns: An observable sequence with the elements skipped
    until the specified start time.
    """
    from rx.core.operators.skipuntilwithtime import _skip_until_with_time
    return _skip_until_with_time(start_time)


def skip_while(predicate: typing.Predicate) -> Callable[[Observable], Observable]:
    """The `skip_while` operator.

    Bypasses elements in an observable sequence as long as a specified
    condition is true and then returns the remaining elements. The
    element's index is used in the logic of the predicate function.

    Example:
        >>> skip_while(lambda value: value < 10)

    Args:
        predicate: A function to test each element for a condition; the
            second parameter of the function represents the index of
            the source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements from
        the input sequence starting at the first element in the linear
        series that does not pass the test specified by predicate.
    """
    from rx.core.operators.skipwhile import _skip_while
    return _skip_while(predicate)


def skip_while_indexed(predicate: typing.PredicateIndexed) -> Callable[[Observable], Observable]:
    """Bypasses elements in an observable sequence as long as a
    specified condition is true and then returns the remaining elements.
    The element's index is used in the logic of the predicate function.

    Example:
        >>> skip_while(lambda value, index: value < 10 or index < 10)

    Args:
        predicate: A function to test each element for a condition; the
            second parameter of the function represents the index of the
            source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements from
        the input sequence starting at the first element in the linear
        series that does not pass the test specified by predicate.
    """
    from rx.core.operators.skipwhile import _skip_while_indexed
    return _skip_while_indexed(predicate)


def skip_with_time(duration: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    """Skips elements for the specified duration from the start of the
    observable source sequence.

    Args:
        >>> res = skip_with_time(5000)

    Specifying a zero value for duration doesn't guarantee no elements
    will be dropped from the start of the source sequence. This is a
    side-effect of the asynchrony introduced by the scheduler, where
    the action that causes callbacks from the source sequence to be
    forwarded may not execute immediately, despite the zero due time.

    Errors produced by the source sequence are always forwarded to the
    result sequence, even if the error occurs before the duration.

    Args:
    duration: Duration for skipping elements from the start of the
        sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements skipped during
        the specified duration from the start of the source sequence.
    """
    from rx.core.operators.skipwithtime import _skip_with_time
    return _skip_with_time(duration)


def slice(start: int = None, stop: int = None, step: int = 1) -> Callable[[Observable], Observable]:
    """The slice operator.

    Slices the given observable. It is basically a wrapper around the
    operators skip(), skip_last(), take(), take_last() and filter().

    This marble diagram helps you remember how slices works with
    streams. Positive numbers is relative to the start of the events,
    while negative numbers are relative to the end (close) of the
    stream.

     r---e---a---c---t---i---v---e---|
     0   1   2   3   4   5   6   7   8
    -8  -7  -6  -5  -4  -3  -2  -1   0

    Examples:
        >>> result = source.slice(1, 10)
        >>> result = source.slice(1, -2)
        >>> result = source.slice(1, -1, 2)

    Args:
        stop:Last element to take of skip last
        step: Takes every step element. Must be larger than zero

    Returns:
        An operator function that takes an observable source and
        returns a sliced observable sequence.
    """
    from rx.core.operators.slice import _slice
    return _slice(start, stop, step)


def some(predicate=None) -> Callable[[Observable], Observable]:
    """The some operator.

    Determines whether some element of an observable sequence satisfies a
    condition if present, else if some items are in the sequence.

    Examples:
        >>> result = source.some()
        >>> result = source.some(lambda x: x > 3)

    Args:
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and
        returnsobservable sequence containing a single element
        determining whether some elements in the source sequence
        pass the test in the specified predicate if given, else if some
        items are in the sequence.
    """
    from rx.core.operators.some import _some
    return _some(predicate)


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


def subscribe_on(scheduler: typing.Scheduler) -> Callable[[Observable], Observable]:
    """Subscribe on the specified scheduler.

    Wrap the source sequence in order to run its subscription and
    unsubscription logic on the specified scheduler. This operation is
    not commonly used; see the remarks section for more information on
    the distinction between subscribe_on and observe_on.

    This only performs the side-effects of subscription and
    unsubscription on the specified scheduler. In order to invoke
    observer callbacks on a scheduler, use observe_on.

    Args:
        scheduler: Scheduler to perform subscription and unsubscription
            actions on.

    Returns:
        An operator function that takes an observable source and
        returns the source sequence whose subscriptions and
        un-subscriptions happen on the specified scheduler.
    """
    from rx.core.operators.subscribeon import _subscribe_on
    return _subscribe_on(scheduler)


def sum(key_mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Computes the sum of a sequence of values that are obtained by
    invoking an optional transform function on each element of the
    input sequence, else if not specified computes the sum on each item
    in the sequence.

    Examples:
        >>> res = sum()
        >>> res = sum(lambda x: x.value)

    Args:
        key_mapper: [Optional] A transform function to apply to each
            element.

    Returns:
        An operator function that takes a source observable and returns
        an observable sequence containing a single element with the sum
        of the values in the source sequence.
    """
    from rx.core.operators.sum import _sum
    return _sum(key_mapper)


def switch_latest() -> Callable[[Observable], Observable]:
    """The switch_latest operator.

    Transforms an observable sequence of observable sequences into an
    observable sequence producing values only from the most recent
    observable sequence.

    Returns:
        A partially applied operator function that takes an observable
        source and returns the observable sequence that at any point in
        time produces the elements of the most recent inner observable
        sequence that has been received.
    """
    from rx.core.operators.switchlatest import _switch_latest
    return _switch_latest()


def take(count: int) -> Callable[[Observable], Observable]:
    """Returns a specified number of contiguous elements from the start
    of an observable sequence.

    Example:
        >>> op = take(5)

    Args:
        count: The number of elements to return.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the specified
        number of elements from the start of the input sequence.
    """
    from rx.core.operators.take import _take
    return _take(count)


def take_last(count: int) -> Callable[[Observable], Observable]:
    """Returns a specified number of contiguous elements from the end
    of an observable sequence.

    Example:
        >>> res = take_last(5)

    This operator accumulates a buffer with a length enough to store
    elements count elements. Upon completion of the source sequence,
    this buffer is drained on the result sequence. This causes the
    elements to be delayed.

    Args:
        count: Number of elements to take from the end of the source
        sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the specified number
        of elements from the end of the source sequence.
    """
    from rx.core.operators.takelast import _take_last
    return _take_last(count)


def take_last_buffer(count) -> Callable[[Observable], Observable]:
    """The `take_last_buffer` operator.

    Returns an array with the specified number of contiguous elements
    from the end of an observable sequence.

    Example:
        >>> res = source.take_last(5)

    This operator accumulates a buffer with a length enough to store
    elements count elements. Upon completion of the source sequence,
    this buffer is drained on the result sequence. This causes the
    elements to be delayed.

    Args:
        count: Number of elements to take from the end of the source
        sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single list with
        the specified number of elements from the end of the source
        sequence.
    """
    from rx.core.operators.takelastbuffer import _take_last_buffer
    return _take_last_buffer(count)


def take_last_with_time(duration) -> Callable[[Observable], Observable]:
    """Returns elements within the specified duration from the end of
    the observable source sequence.

    Example:
        >>> res = take_last_with_time(5000)

    This operator accumulates a queue with a length enough to store
    elements received during the initial duration window. As more
    elements are received, elements older than the specified duration
    are taken from the queue and produced on the result sequence. This
    causes elements to be delayed with duration.

    Args:
        duration: Duration for taking elements from the end of the
        sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements taken
        during the specified duration from the end of the source
        sequence.
    """
    from rx.core.operators.takelastwithtime import _take_last_with_time
    return _take_last_with_time(duration)


def take_until(other: Observable) -> Callable[[Observable], Observable]:
    """Returns the values from the source observable sequence until the
    other observable sequence produces a value.

    Args:
        other: Observable sequence that terminates propagation of
            elements of the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns as observable sequence containing the elements of the
        source sequence up to the point the other sequence interrupted
        further propagation.
    """
    from rx.core.operators.takeuntil import _take_until
    return _take_until(other)


def take_until_with_time(end_time: Union[datetime, int], scheduler: typing.Scheduler = None
                         ) -> Callable[[Observable], Observable]:
    """Takes elements for the specified duration until the specified end
    time, using the specified scheduler to run timers.

    Examples:
        >>> res = source.take_until_with_time(dt, [optional scheduler])
        >>> res = source.take_until_with_time(5000, [optional scheduler])

    Args:
        end_time: Time to stop taking elements from the source
            sequence. If this value is less than or equal to
            `datetime.utcnow()`, the result stream will complete
            immediately.
        scheduler: Scheduler to run the timer on.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements taken until
        the specified end time.
    """
    from rx.core.operators.takeuntilwithtime import _take_until_with_time
    return _take_until_with_time(end_time, scheduler)


def take_while(predicate: Callable[[Any], Any]) -> Callable[[Observable], Observable]:
    """Returns elements from an observable sequence as long as a
    specified condition is true. The element's index is used in the
    logic of the predicate function.

    Example:
        >>> take_while(lambda value: value < 10)

    Args:
        predicate: A function to test each element for a condition; the
            second parameter of the function represents the index of
            the source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements from
        the input sequence that occur before the element at which the
        test no longer passes.
    """
    from rx.core.operators.takewhile import _take_while
    return _take_while(predicate)


def take_while_indexed(predicate: Callable[[Any, int], Any]) -> Callable[[Observable], Observable]:
    """Returns elements from an observable sequence as long as a specified
    condition is true. The element's index is used in the logic of the
    predicate function.

    Example:
        >>> take_while(lambda value, index: value < 10 or index < 10)

    Args:
        predicate: A function to test each element for a condition; the
        second parameter of the function represents the index of the source
        element.

    Returns:
        An observable sequence that contains the elements from the
    input sequence that occur before the element at which the test no
    longer passes.
    """
    from rx.core.operators.takewhile import _take_while_indexed
    return _take_while_indexed(predicate)


def take_with_time(duration: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    """Takes elements for the specified duration from the start of the
    observable source sequence.

    Example:
        >>> res = take_with_time(5000)

    This operator accumulates a queue with a length enough to store
    elements received during the initial duration window. As more
    elements are received, elements older than the specified duration
    are taken from the queue and produced on the result sequence. This
    causes elements to be delayed with duration.

    Args:
        duration: Duration for taking elements from the start of the
            sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements taken during
        the specified duration from the start of the source sequence.
    """
    from rx.core.operators.takewithtime import _take_with_time
    return _take_with_time(duration)


def throttle_first(window_duration: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    """Returns an Observable that emits only the first item emitted by
    the source Observable during sequential time windows of a specified
    duration.

    Args:
        window_duration: time to wait before emitting another item
            after emitting the last item.

    Returns:
        An operator function that takes an observable source and
        returns an observable that performs the throttle operation.
    """
    from rx.core.operators.throttlefirst import _throttle_first
    return _throttle_first(window_duration)


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


def timeout(duetime: Union[int, datetime], other: Observable = None, scheduler: typing.Scheduler = None
            ) -> Callable[[Observable], Observable]:
    """Returns the source observable sequence or the other observable
    sequence if duetime elapses.

    Examples:
        >>> res = timeout(5000)
        >>> res = timeout(datetime(), return_value(42))
        >>> res = timeout(5000, return_value(42))

    Args:
        duetime: Absolute (specified as a datetime object) or relative
            time (specified as an integer denoting milliseconds) when a
            timeout occurs.
        other: Sequence to return in case of a timeout. If not
            specified, a timeout error throwing sequence will be used.
        scheduler:

    Returns:
        An operator function that takes and observable source and
        returns the source sequence switching to the other sequence in
        case of a timeout.
    """
    from rx.core.operators.timeout import _timeout
    return _timeout(duetime, other, scheduler)


def timeout_with_mapper(first_timeout=None, timeout_duration_mapper=None, other=None
                       ) -> Callable[[Observable], Observable]:
    """Returns the source observable sequence, switching to the other
    observable sequence if a timeout is signaled.

        res = timeout_with_mapper(rx.timer(500))
        res = timeout_with_mapper(rx.timer(500), lambda x: rx.timer(200))
        res = timeout_with_mapper(rx.timer(500), lambda x: rx.timer(200)), rx.return_value(42))

    Args:
        first_timeout: [Optional] Observable sequence that represents
            the timeout for the first element. If not provided, this
            defaults to rx.never().
        timeout_duration_mapper: [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the
            current element and the next element.
        other: [Optional] Sequence to return in case of a timeout. If
            not provided, this is set to rx.throw().

    Returns:
        An operator function that takes an observable source and
        returns the source sequence switching to the other sequence in
        case of a timeout.
    """
    from rx.core.operators.timeoutwithmapper import _timeout_with_mapper
    return _timeout_with_mapper(first_timeout, timeout_duration_mapper, other)


def time_interval() -> Callable[[Observable], Observable]:
    """Records the time interval between consecutive values in an
    observable sequence.

        >>> res = time_interval()

    Return:
        An operator function that takes an observable source and
        returns an observable sequence with time interval information
        on values.
    """
    from rx.core.operators.timeinterval import _time_interval
    return _time_interval()


def to_blocking() -> Callable[[Observable], BlockingObservable]:
    from rx.core.operators.toblocking import _to_blocking
    return _to_blocking()


def to_dict(key_mapper: Callable[[Any], Any], element_mapper: Callable[[Any], Any] = None
           ) -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a Map if it exists.

    Args:
        key_mapper: A function which produces the key for the
            dictionary.
        element_mapper: [Optional] An optional function which produces
            the element for the dictionary. If not present, defaults to
            the value from the observable sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with a single value of a
        dictionary containing the values from the observable sequence.
    """
    from rx.core.operators.todict import _to_dict
    return _to_dict(key_mapper, element_mapper)


def to_future(future_ctor: Callable[[], Future] = None) -> Callable[[Observable], Future]:
    """Converts an existing observable sequence to a Future.

    Example:
        op = to_future(asyncio.Future);

    Args:
        future_ctor: [Optional] The constructor of the future.

    Returns:
        An operator function that takes an obserable source and returns
        a future with the last value from the observable sequence.
    """
    from rx.core.operators.tofuture import _to_future
    return _to_future(future_ctor)


def to_iterable() -> Callable[[Observable], Observable]:
    """Creates an iterable from an observable sequence.

    Returns:
        An operator function that takes an obserable source and
        returns an observable sequence containing a single element with
        an iterable containing all the elements of the source sequence.
    """
    from rx.core.operators.toiterable import _to_iterable
    return _to_iterable()


def to_set() -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a set.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with a single value of a set
        containing the values from the observable sequence.
    """
    from rx.core.operators.toset import _to_set
    return _to_set()


def while_do(condition) -> Callable[[Observable], Observable]:
    """Repeats source as long as condition holds emulating a while
    loop.

    Args:
        condition: The condition which determines if the source will be
            repeated.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence which is repeated as long as the
        condition holds.
    """
    from rx.core.operators.whiledo import _while_do
    return _while_do(condition)


def window(window_openings=None, window_closing_mapper=None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        window_openings: Observable sequence whose elements denote the
            creation of windows.
        window_closing_mapper: [Optional] A function invoked to define
            the closing of each produced window. It defines the
            boundaries of the produced windows (a window is started
            when the previous one is closed, resulting in
            non-overlapping windows).

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of windows.
    """
    from rx.core.operators.window import _window
    return _window(window_openings, window_closing_mapper)


def window_with_count(count: int, skip: int = None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on element count information.

    Examples:
        >>> window_with_count(10)
        >>> window_with_count(10, 1)

    Args:
        count: Length of each window.
        skip: [Optional] Number of elements to skip between creation of
            consecutive windows. If not specified, defaults to the
            count.

    Returns:
        An observable sequence of windows.
    """
    from rx.core.operators.windowwithcount import _window_with_count
    return _window_with_count(count, skip)


def window_with_time(timespan: Union[timedelta, int], timeshift: Union[timedelta, int] = None,
                      scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    from rx.core.operators.windowwithtime import _window_with_time
    return _window_with_time(timespan, timeshift, scheduler)


def window_with_time_or_count(timespan: Union[timedelta, int], count: int, scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    from rx.core.operators.windowwithtimeorcount import _window_with_time_or_count
    return _window_with_time_or_count(timespan, count, scheduler)


def with_latest_from(*args: Union[Observable, Iterable[Observable]], mapper: Callable[[Any], Any]
                    ) -> Callable[[Observable], Observable]:
    """The `with_latest_from` operator.

    Merges the specified observable sequences into one observable
    sequence by using the mapper function only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    Examples:
        >>> op = with_latest_from(obs1, lambda o1: o1)
        >>> op = with_latest_from([obs1, obs2, obs3], lambda o1, o2, o3: o1 + o2 + o3)

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
    """
    from rx.core.operators.withlatestfrom import _with_latest_from
    return _with_latest_from(*args, mapper=mapper)


def zip(*args: Observable, result_mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Merges the specified observable sequences into one observable
    sequence by using the mapper function whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    The last element in the arguments must be a function to invoke for
    each series of elements at corresponding indexes in the sources.

    Example:
        >>> res = zip(obs1, obs2, result_mapper=fn)

    Args:
        args: Observable sources to zip.
        result_mapper: Mapper function that produces an element
            whenever all of the observable sequences have produced an
            element at a corresponding index

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
    """
    from rx.core.operators.zip import _zip
    return _zip(*args, result_mapper=result_mapper)


def zip_with_iterable(second, result_mapper):
    """Merges the specified observable sequence and list into one
    observable sequence by using the mapper function whenever all of
    the observable sequences have produced an element at a
    corresponding index.

    The result mapper must be a function to invoke for each series of
    elements at corresponding indexes in the sources.

    Example
        >>> res = zip(xs, [1,2,3], result_mapper=fn)

    Args:
        second: Iterable to zip.
        result_mapper: Mapper function that produces an element
            whenever all of the observable sequences have produced an
            element at a corresponding index

    Returns:
        An operator function that takes and observable source and
        returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
    """
    from rx.core.operators.zip import _zip_with_iterable
    return _zip_with_iterable(second, result_mapper)


zip_with_list = zip_with_iterable
