# pylint: disable=too-many-lines
from typing import Callable, Union, Any, Iterable, List
from datetime import timedelta, datetime

from rx.core import Observable, ConnectableObservable, typing
from rx.core.typing import Mapper, MapperIndexed, Predicate, PredicateIndexed
from rx.subjects import Subject


# pylint: disable=redefined-builtin
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


def combine_latest(other: Union[Observable, Iterable[Observable]],
                   mapper: Callable[[Any], Any]) -> Callable[[Observable], Observable]:
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


def is_empty() -> Callable[[Observable], Observable]:
    """Determines whether an observable sequence is empty.

    Returns:
        An observable sequence containing a single element
        determining whether the source sequence is empty.
    """
    from rx.core.operators.isempty import _is_empty
    return _is_empty()


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
    return _min_by(comparer)

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
        predicate -- [Optional] A predicate function to evaluate for
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
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- [Optional] The default value if the index is
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
        predicate -- A function to test each element for a condition.

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

def sum(key_mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Computes the sum of a sequence of values that are obtained by
    invoking an optional transform function on each element of the
    input sequence, else if not specified computes the sum on each item
    in the sequence.

    Examples:
        >>> res = sum()
        >>> res = sum(lambda x: x.value)

    Args:
        key_mapper -- [Optional] A transform function to apply to each
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
        scheduler -- Scheduler to run the timer on.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements taken until
        the specified end time.
    """
    from rx.core.operators.takeuntilwithtime import _take_until_with_time
    return _take_until_with_time(end_time, scheduler=None)


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


def to_iterable() -> Callable[[Observable], Observable]:
    """Creates an iterable from an observable sequence.

    Returns:
        An operator function that takes an obserable source and
        returns an observable sequence containing a single element with
        an iterable containing all the elements of the source sequence.
    """
    from rx.core.operators.toiterable import _to_iterable
    return _to_iterable()


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
        second -- Iterable to zip.
        result_mapper -- Mapper function that produces an element
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
