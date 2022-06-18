# pylint: disable=too-many-lines,redefined-builtin,import-outside-toplevel


from asyncio import Future
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from reactivex import (
    ConnectableObservable,
    GroupedObservable,
    Notification,
    Observable,
    abc,
    compose,
    typing,
)
from reactivex.internal.basic import identity
from reactivex.internal.utils import NotSet
from reactivex.subject import Subject
from reactivex.typing import (
    Accumulator,
    Comparer,
    Mapper,
    MapperIndexed,
    Predicate,
    PredicateIndexed,
)

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_TKey = TypeVar("_TKey")
_TState = TypeVar("_TState")
_TValue = TypeVar("_TValue")
_TRight = TypeVar("_TRight")
_TLeft = TypeVar("_TLeft")

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")


def all(predicate: Predicate[_T]) -> Callable[[Observable[_T]], Observable[bool]]:
    """Determines whether all elements of an observable sequence satisfy
    a condition.

    .. marble::
        :alt: all

        --1--2--3--4--5-|
        [      all(i: i<10)    ]
        ----------------true-|

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
    from ._all import all_

    return all_(predicate)


def amb(right_source: Observable[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Propagates the observable sequence that reacts first.

    .. marble::
        :alt: amb

        ---8--6--9-----------|
        --1--2--3---5--------|
        ----------10-20-30---|
        [        amb()       ]
        --1--2--3---5--------|

    Example:
        >>> op = amb(ys)

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that surfaces any of the given
        sequences, whichever reacted first.
    """
    from ._amb import amb_

    return amb_(right_source)


def as_observable() -> Callable[[Observable[_T]], Observable[_T]]:
    """Hides the identity of an observable sequence.

    Returns:
        An operator function that takes an observable source and
        returns and observable sequence that hides the identity of the
        source sequence.
    """
    from ._asobservable import as_observable_

    return as_observable_()


def average(
    key_mapper: Optional[Mapper[_T, float]] = None
) -> Callable[[Observable[_T]], Observable[float]]:
    """The average operator.

    Computes the average of an observable sequence of values that
    are in the sequence or obtained by invoking a transform function on
    each element of the input sequence if present.

    .. marble::
        :alt: average

        ---1--2--3--4----|
        [     average()      ]
        -----------------2.5-|

    Examples:
        >>> op = average()
        >>> op = average(lambda x: x.value)

    Args:
        key_mapper: [Optional] A transform function to apply to each element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element with
        the average of the sequence of values.
    """
    from ._average import average_

    return average_(key_mapper)


def buffer(
    boundaries: Observable[Any],
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into zero or
    more buffers.

    .. marble::
        :alt: buffer

        ---a-----b-----c--------|
        --1--2--3--4--5--6--7---|
        [       buffer()        ]
        ---1-----2,3---4,5------|

    Examples:
        >>> res = buffer(reactivex.interval(1.0))

    Args:
        boundaries: Observable sequence whose elements denote the
            creation and completion of buffers.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """
    from ._buffer import buffer_

    return buffer_(boundaries)


def buffer_when(
    closing_mapper: Callable[[], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into zero or
    more buffers.

    .. marble::
        :alt: buffer_when

        --------c-|
                --------c-|
                        --------c-|
        ---1--2--3--4--5--6-------|
        [      buffer_when()      ]
        +-------1,2-----3,4,5---6-|

    Examples:
        >>> res = buffer_when(lambda: reactivex.timer(0.5))

    Args:
        closing_mapper: A function invoked to define the closing of each
            produced buffer. A buffer is started when the previous one is
            closed, resulting in non-overlapping buffers. The buffer is closed
            when one item is emitted or when the observable completes.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of windows.
    """
    from ._buffer import buffer_when_

    return buffer_when_(closing_mapper)


def buffer_toggle(
    openings: Observable[Any], closing_mapper: Callable[[Any], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into zero or
    more buffers.

    .. marble::
        :alt: buffer_toggle

        ---a-----------b--------------|
           ---d--|
                       --------e--|
        ----1--2--3--4--5--6--7--8----|
        [       buffer_toggle()       ]
        ------1----------------5,6,7--|

    >>> res = buffer_toggle(reactivex.interval(0.5), lambda i: reactivex.timer(i))

    Args:
        openings: Observable sequence whose elements denote the
            creation of buffers.
        closing_mapper: A function invoked to define the closing of each
            produced buffer. Value from openings Observable that initiated
            the associated buffer is provided as argument to the function. The
            buffer is closed when one item is emitted or when the observable
            completes.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of windows.
    """
    from ._buffer import buffer_toggle_

    return buffer_toggle_(openings, closing_mapper)


def buffer_with_count(
    count: int, skip: Optional[int] = None
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    .. marble::
        :alt: buffer_with_count

        ----1-2-3-4-5-6------|
        [buffer_with_count(3)]
        --------1,2,3-4,5,6--|

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
    from ._buffer import buffer_with_count_

    return buffer_with_count_(count, skip)


def buffer_with_time(
    timespan: typing.RelativeTime,
    timeshift: Optional[typing.RelativeTime] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on timing information.

    .. marble::
        :alt: buffer_with_time

        ---1-2-3-4-5-6-----|
        [buffer_with_time()]
        -------1,2,3-4,5,6-|

    Examples:
        >>> # non-overlapping segments of 1 second
        >>> res = buffer_with_time(1.0)
        >>> # segments of 1 second with time shift 0.5 seconds
        >>> res = buffer_with_time(1.0, 0.5)

    Args:
        timespan: Length of each buffer (specified as a float denoting seconds
            or an instance of timedelta).
        timeshift: [Optional] Interval between creation of consecutive buffers
            (specified as a float denoting seconds or an instance of timedelta).
            If not specified, the timeshift will be the same as the timespan
            argument, resulting in non-overlapping adjacent buffers.
        scheduler:  [Optional] Scheduler to run the timer on. If not specified,
             the timeout scheduler is used

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of buffers.
    """
    from ._bufferwithtime import buffer_with_time_

    return buffer_with_time_(timespan, timeshift, scheduler)


def buffer_with_time_or_count(
    timespan: typing.RelativeTime,
    count: int,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Projects each element of an observable sequence into a buffer
    that is completed when either it's full or a given amount of time
    has elapsed.

    .. marble::
        :alt: buffer_with_time_or_count

        --1-2-3-4-5-6------|
        [     buffer()     ]
        ------1,2,3-4,5,6--|

    Examples:
        >>> # 5s or 50 items in an array
        >>> res = source._buffer_with_time_or_count(5.0, 50)
        >>> # 5s or 50 items in an array
        >>> res = source._buffer_with_time_or_count(5.0, 50, Scheduler.timeout)

    Args:
        timespan: Maximum time length of a buffer.
        count: Maximum element count of a buffer.
        scheduler: [Optional] Scheduler to run buffering timers on. If
            not specified, the timeout scheduler is used.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of buffers.
    """
    from ._bufferwithtimeorcount import buffer_with_time_or_count_

    return buffer_with_time_or_count_(timespan, count, scheduler)


def catch(
    handler: Union[
        Observable[_T], Callable[[Exception, Observable[_T]], Observable[_T]]
    ]
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    .. marble::
        :alt: catch

        ---1---2---3-*
                     a-7-8-|
        [      catch(a)    ]
        ---1---2---3---7-8-|

    Examples:
        >>> op = catch(ys)
        >>> op = catch(lambda ex, src: ys(ex))

    Args:
        handler: Second observable sequence used to produce
            results when an error occurred in the first sequence, or an
            exception handler function that returns an observable sequence
            given the error and source observable that occurred in the
            first sequence.

    Returns:
        A function taking an observable source and returns an
        observable sequence containing the first sequence's elements,
        followed by the elements of the handler sequence in case an
        exception occurred.
    """
    from ._catch import catch_

    return catch_(handler)


def combine_latest(
    *others: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Any]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the
    observable sequences produces an element.

    .. marble::
        :alt: combine_latest

        ---a-----b--c------|
        --1---2--------3---|
        [ combine_latest() ]
        ---a1-a2-b2-c2-c3--|

    Examples:
        >>> obs = combine_latest(other)
        >>> obs = combine_latest(obs1, obs2, obs3)

    Returns:
        An operator function that takes an observable sources and
        returns an observable sequence containing the result of
        combining elements of the sources into a tuple.
    """
    from ._combinelatest import combine_latest_

    return combine_latest_(*others)


def concat(*sources: Observable[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Concatenates all the observable sequences.

    .. marble::
        :alt: concat

        ---1--2--3--|
        --6--8--|
        [     concat()     ]
        ---1--2--3----6--8-|

    Examples:
        >>> op = concat(xs, ys, zs)

    Returns:
        An operator function that takes one or more observable sources and
        returns an observable sequence that contains the elements of
        each given sequence, in sequential order.
    """
    from ._concat import concat_

    return concat_(*sources)


def contains(
    value: _T, comparer: Optional[typing.Comparer[_T]] = None
) -> Callable[[Observable[_T]], Observable[bool]]:
    """Determines whether an observable sequence contains a specified
    element with an optional equality comparer.

    .. marble::
        :alt: contains

        --1--2--3--4--|
        [    contains(3)   ]
        --------------true-|

    Examples:
        >>> op = contains(42)
        >>> op = contains({ "value": 42 }, lambda x, y: x["value"] == y["value"])

    Args:
        value: The value to locate in the source sequence.
        comparer: [Optional] An equality comparer to compare elements.

    Returns:
        A function that takes a source observable that returns an
        observable  sequence containing a single element determining
        whether the source sequence contains an element that has the
        specified value.
    """
    from ._contains import contains_

    return contains_(value, comparer)


def count(
    predicate: Optional[typing.Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[int]]:
    """Returns an observable sequence containing a value that
    represents how many elements in the specified observable sequence
    satisfy a condition if provided, else the count of items.

    .. marble::
        :alt: count

        --1--2--3--4--|
        [  count(i: i>2)   ]
        --------------2-|

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

    from ._count import count_

    return count_(predicate)


def debounce(
    duetime: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    .. marble::
        :alt: debounce

        --1--2-3-4--5------|
        [    debounce()    ]
        ----1------4---5---|

    Example:
        >>> res = debounce(5.0) # 5 seconds

    Args:
        duetime: Duration of the throttle period for each value
            (specified as a float denoting seconds or an instance of timedelta).
        scheduler: Scheduler to debounce values on.

    Returns:
        An operator function that takes the source observable and
        returns the debounced observable sequence.
    """
    from ._debounce import debounce_

    return debounce_(duetime, scheduler)


throttle_with_timeout = debounce


@overload
def default_if_empty(
    default_value: _T,
) -> Callable[[Observable[_T]], Observable[_T]]:
    ...


@overload
def default_if_empty() -> Callable[[Observable[_T]], Observable[Optional[_T]]]:
    ...


def default_if_empty(
    default_value: Any = None,
) -> Callable[[Observable[Any]], Observable[Any]]:
    """Returns the elements of the specified sequence or the specified
    value in a singleton sequence if the sequence is empty.

    .. marble::
        :alt: default_if_empty

        ----------|
        [default_if_empty(42)]
        ----------42-|

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
    from ._defaultifempty import default_if_empty_

    return default_if_empty_(default_value)


def delay_subscription(
    duetime: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Time shifts the observable sequence by delaying the
    subscription.

    .. marble::
        :alt: delay_subscription

        ----1--2--3--4-----|
        [     delay()      ]
        --------1--2--3--4-|

    Example:
        >>> res = delay_subscription(5.0) # 5s

    Args:
        duetime: Absolute or relative time to perform the subscription
        at.
        scheduler: Scheduler to delay subscription on.

    Returns:
        A function that take a source observable and returns a
        time-shifted observable sequence.
    """
    from ._delaysubscription import delay_subscription_

    return delay_subscription_(duetime, scheduler=scheduler)


def delay_with_mapper(
    subscription_delay: Union[
        Observable[Any],
        typing.Mapper[Any, Observable[Any]],
        None,
    ] = None,
    delay_duration_mapper: Optional[typing.Mapper[_T, Observable[Any]]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Time shifts the observable sequence based on a subscription
    delay and a delay mapper function for each element.

    .. marble::
        :alt: delay_with_mapper

        ----1--2--3--4-----|
        [     delay()      ]
        --------1--2--3--4-|

    Examples:
        >>> # with mapper only
        >>> res = source.delay_with_mapper(lambda x: Scheduler.timer(5.0))
        >>> # with delay and mapper
        >>> res = source.delay_with_mapper(
            reactivex.timer(2.0), lambda x: reactivex.timer(x)
        )

    Args:
        subscription_delay: [Optional] Sequence indicating the delay
            for the subscription to the source.
        delay_duration_mapper: [Optional] Selector function to retrieve
            a sequence indicating the delay for each given element.

    Returns:
        A function that takes an observable source and returns a
        time-shifted observable sequence.
    """
    from ._delaywithmapper import delay_with_mapper_

    return delay_with_mapper_(subscription_delay, delay_duration_mapper)


def dematerialize() -> Callable[[Observable[Notification[_T]]], Observable[_T]]:
    """Dematerialize operator.

    Dematerializes the explicit notification values of an
    observable sequence as implicit notifications.

    Returns:
        An observable sequence exhibiting the behavior
        corresponding to the source sequence's notification values.
    """
    from ._dematerialize import dematerialize_

    return dematerialize_()


def delay(
    duetime: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The delay operator.

    .. marble::
        :alt: delay

        ----1--2--3--4-----|
        [     delay()      ]
        --------1--2--3--4-|

    Time shifts the observable sequence by duetime. The relative time
    intervals between the values are preserved.

    Examples:
        >>> res = delay(timedelta(seconds=10))
        >>> res = delay(5.0)

    Args:
        duetime: Relative time, specified as a float denoting seconds or an
            instance of timedelta, by which to shift the observable sequence.
        scheduler: [Optional] Scheduler to run the delay timers on.
            If not specified, the timeout scheduler is used.

    Returns:
        A partially applied operator function that takes the source
        observable and returns a time-shifted sequence.
    """
    from ._delay import delay_

    return delay_(duetime, scheduler)


def distinct(
    key_mapper: Optional[Mapper[_T, _TKey]] = None,
    comparer: Optional[Comparer[_TKey]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns an observable sequence that contains only distinct
    elements according to the key_mapper and the comparer. Usage of
    this operator should be considered carefully due to the maintenance
    of an internal lookup structure which can grow large.

    .. marble::
        :alt: distinct

        -0-1-2-1-3-4-2-0---|
        [    distinct()    ]
        -0-1-2---3-4-------|


    Examples:
        >>> res = obs = xs.distinct()
        >>> obs = xs.distinct(lambda x: x.id)
        >>> obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)

    Args:
        key_mapper: [Optional]  A function to compute the comparison
            key for each element.
        comparer: [Optional]  Used to compare items in the collection.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence only containing the distinct
        elements, based on a computed key value, from the source
        sequence.
    """
    from ._distinct import distinct_

    return distinct_(key_mapper, comparer)


def distinct_until_changed(
    key_mapper: Optional[Mapper[_T, _TKey]] = None,
    comparer: Optional[Comparer[_TKey]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns an observable sequence that contains only distinct
    contiguous elements according to the key_mapper and the comparer.

    .. marble::
        :alt: distinct_until_changed

        -0-1-1-2-3-1-2-2-3-|
        [    distinct()    ]
        -0-1---2-3-1-2---3-|


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
    from ._distinctuntilchanged import distinct_until_changed_

    return distinct_until_changed_(key_mapper, comparer)


def do(observer: abc.ObserverBase[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Invokes an action for each element in the observable sequence
    and invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging,
    logging, etc. of query behavior by intercepting the message stream
    to run arbitrary actions for messages on the pipeline.

    .. marble::
        :alt: do

        ----1---2---3---4---|
        [    do(i: foo())   ]
        ----1---2---3---4---|


    >>> do(observer)

    Args:
        observer: Observer

    Returns:
        An operator function that takes the source observable and
        returns the source sequence with the side-effecting behavior
        applied.
    """
    from ._do import do_

    return do_(observer)


def do_action(
    on_next: Optional[typing.OnNext[_T]] = None,
    on_error: Optional[typing.OnError] = None,
    on_completed: Optional[typing.OnCompleted] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Invokes an action for each element in the observable sequence
    and invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging,
    logging, etc. of query behavior by intercepting the message stream
    to run arbitrary actions for messages on the pipeline.

    .. marble::
        :alt: do_action

        ----1---2---3---4---|
        [do_action(i: foo())]
        ----1---2---3---4---|

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
    from ._do import do_action_

    return do_action_(on_next, on_error, on_completed)


def do_while(
    condition: Predicate[Observable[_T]],
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Repeats source as long as condition holds emulating a do while
    loop.

    .. marble::
        :alt: do_while

        --1--2--|
        [    do_while()     ]
        --1--2--1--2--1--2--|


    Args:
        condition: The condition which determines if the source will be
            repeated.

    Returns:
        An observable sequence which is repeated as long
        as the condition holds.
    """
    from ._dowhile import do_while_

    return do_while_(condition)


def element_at(index: int) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the element at a specified index in a sequence.

    .. marble::
        :alt: element_at

        ----1---2---3---4---|
        [   element_at(2)   ]
        ------------3-|

    Example:
        >>> res = source.element_at(5)

    Args:
        index: The zero-based index of the element to retrieve.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that produces the element at
        the specified position in the source sequence.
    """
    from ._elementatordefault import element_at_or_default_

    return element_at_or_default_(index, False)


def element_at_or_default(
    index: int, default_value: Optional[_T] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the element at a specified index in a sequence or a
    default value if the index is out of range.

    .. marble::
        :alt: element_at_or_default

        --1---2---3---4-|
        [  element_at(6, a) ]
        ----------------a-|

    Example:
        >>> res = source.element_at_or_default(5)
        >>> res = source.element_at_or_default(5, 0)

    Args:
        index: The zero-based index of the element to retrieve.
        default_value: [Optional] The default value if the index is
            outside the bounds of the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence that produces the element at the
        specified position in the source sequence, or a default value if
        the index is outside the bounds of the source sequence.
    """
    from ._elementatordefault import element_at_or_default_

    return element_at_or_default_(index, True, default_value)


def exclusive() -> Callable[[Observable[Observable[_T]]], Observable[_T]]:
    """Performs a exclusive waiting for the first to finish before
    subscribing to another observable. Observables that come in between
    subscriptions will be dropped on the floor.

    .. marble::
        :alt: exclusive

        -+---+-----+-------|
                   +-7-8-9-|
             +-4-5-6-|
         +-1-2-3-|
        [   exclusive()    ]
        ---1-2-3-----7-8-9-|


    Returns:
        An exclusive observable with only the results that
        happen when subscribed.
    """
    from ._exclusive import exclusive_

    return exclusive_()


def expand(
    mapper: typing.Mapper[_T, Observable[_T]]
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Expands an observable sequence by recursively invoking mapper.

    Args:
        mapper: Mapper function to invoke for each produced element,
            resulting in another sequence to which the mapper will be
            invoked recursively again.

    Returns:
        An observable sequence containing all the elements produced
    by the recursive expansion.
    """
    from ._expand import expand_

    return expand_(mapper)


def filter(predicate: Predicate[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Filters the elements of an observable sequence based on a
    predicate.

    .. marble::
        :alt: filter

        ----1---2---3---4---|
        [   filter(i: i>2)  ]
        ------------3---4---|

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
    from ._filter import filter_

    return filter_(predicate)


def filter_indexed(
    predicate_indexed: Optional[PredicateIndexed[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    .. marble::
        :alt: filter_indexed

        ----1---2---3---4---|
        [ filter(i,id: id>2)]
        ----------------4---|

    Example:
        >>> op = filter_indexed(lambda value, index: (value + index) < 10)

    Args:
        predicate: A function to test each source element for a
            condition; the second parameter of the function represents
            the index of the source element.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains elements from the
        input sequence that satisfy the condition.
    """
    from ._filter import filter_indexed_

    return filter_indexed_(predicate_indexed)


def finally_action(action: typing.Action) -> Callable[[Observable[_T]], Observable[_T]]:
    """Invokes a specified action after the source observable sequence
    terminates gracefully or exceptionally.

    .. marble::
        :alt: finally_action

        --1--2--3--4--|
                  a-6-7-|
        [finally_action(a)]
        --1--2--3--4--6-7-|

    Example:
        >>> res = finally_action(lambda: print('sequence ended')

    Args:
        action: Action to invoke after the source observable sequence
            terminates.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the action-invoking
        termination behavior applied.
    """
    from ._finallyaction import finally_action_

    return finally_action_(action)


def find(
    predicate: Callable[[_T, int, Observable[_T]], bool]
) -> Callable[[Observable[_T]], Observable[Union[_T, None]]]:
    """Searches for an element that matches the conditions defined by
    the specified predicate, and returns the first occurrence within
    the entire Observable sequence.

    .. marble::
        :alt: find

        --1--2--3--4--3--2--|
        [       find(3)     ]
        --------3-|

    Args:
        predicate: The predicate that defines the conditions of the
            element to search for.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the first element that
        matches the conditions defined by the specified predicate, if
        found otherwise, None.
    """
    from ._find import find_value_

    return cast(
        Callable[[Observable[_T]], Observable[Union[_T, None]]],
        find_value_(predicate, False),
    )


def find_index(
    predicate: Callable[[_T, int, Observable[_T]], bool]
) -> Callable[[Observable[_T]], Observable[Union[int, None]]]:
    """Searches for an element that matches the conditions defined by
    the specified predicate, and returns an Observable sequence with the
    zero-based index of the first occurrence within the entire
    Observable sequence.

    .. marble::
        :alt: find_index

        --1--2--3--4--3--2--|
        [   find_index(3)   ]
        --------2-|

    Args:
        predicate: The predicate that defines the conditions of the
            element to search for.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the zero-based index of the
        first occurrence of an element that matches the conditions
        defined by match, if found; otherwise, -1.
    """
    from ._find import find_value_

    return cast(
        Callable[[Observable[_T]], Observable[Union[int, None]]],
        find_value_(predicate, True),
    )


def first(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    .. marble::
        :alt: first

        ---1---2---3---4----|
        [   first(i: i>1)   ]
        -------2-|


    Examples:
        >>> res = res = first()
        >>> res = res = first(lambda x: x > 3)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the
        predicate if provided, else the first item in the sequence.
    """
    from ._first import first_

    return first_(predicate)


def first_or_default(
    predicate: Optional[Predicate[_T]] = None, default_value: Optional[_T] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate, or a default value if no
    such element exists.

    .. marble::
        :alt: first_or_default

        --1--2--3--4-|
        [first(i: i>10, 42)]
        -------------42-|

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
        A function that takes an observable source and returns an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
    """
    from ._firstordefault import first_or_default_

    return first_or_default_(predicate, default_value)


@overload
def flat_map(
    mapper: Optional[Iterable[_T2]] = None,
) -> Callable[[Observable[Any]], Observable[_T2]]:
    ...


@overload
def flat_map(
    mapper: Optional[Observable[_T2]] = None,
) -> Callable[[Observable[Any]], Observable[_T2]]:
    ...


@overload
def flat_map(
    mapper: Optional[Mapper[_T1, Iterable[_T2]]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


@overload
def flat_map(
    mapper: Optional[Mapper[_T1, Observable[_T2]]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


def flat_map(
    mapper: Optional[Any] = None,
) -> Callable[[Observable[Any]], Observable[Any]]:
    """The flat_map operator.

    .. marble::
        :alt: flat_map

        --1-2-3-|
        [ flat_map(range)  ]
        --0-0-1-0-1-2-|


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
    from ._flatmap import flat_map_

    return flat_map_(mapper)


@overload
def flat_map_indexed(
    mapper_indexed: Optional[Iterable[_T2]] = None,
) -> Callable[[Observable[Any]], Observable[_T2]]:
    ...


@overload
def flat_map_indexed(
    mapper_indexed: Optional[Observable[_T2]] = None,
) -> Callable[[Observable[Any]], Observable[_T2]]:
    ...


@overload
def flat_map_indexed(
    mapper_indexed: Optional[MapperIndexed[_T1, Iterable[_T2]]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


@overload
def flat_map_indexed(
    mapper_indexed: Optional[MapperIndexed[_T1, Observable[_T2]]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


def flat_map_indexed(
    mapper_indexed: Any = None,
) -> Callable[[Observable[Any]], Observable[Any]]:
    """The `flat_map_indexed` operator.

    One of the Following:
    Projects each element of an observable sequence to an observable
    sequence and merges the resulting observable sequences into one
    observable sequence.

    .. marble::
        :alt: flat_map_indexed

        --1-2-3-|
        [ flat_map(range)  ]
        --0-0-1-0-1-2-|

    Example:
        >>> source.flat_map_indexed(lambda x, i: Observable.range(0, x))

    Or:
    Projects each element of the source observable sequence to the
    other observable sequence and merges the resulting observable
    sequences into one observable sequence.

    Example:
        >>> source.flat_map_indexed(Observable.of(1, 2, 3))

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
    from ._flatmap import flat_map_indexed_

    return flat_map_indexed_(mapper_indexed)


def flat_map_latest(
    mapper: Mapper[_T1, Union[Observable[_T2], "Future[_T2]"]]
) -> Callable[[Observable[_T1]], Observable[_T2]]:
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
    from ._flatmap import flat_map_latest_

    return flat_map_latest_(mapper)


def fork_join(
    *others: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Tuple[Any, ...]]]:
    """Wait for observables to complete and then combine last values
    they emitted into a tuple. Whenever any of that observables completes
    without emitting any value, result sequence will complete at that moment as well.

    .. marble::
        :alt: fork_join

        ---a-----b--c---d-|
        --1---2------3-4---|
        -a---------b---|
        [      fork_join()     ]
        --------------------d4b|

    Examples:
        >>> res = fork_join(obs1)
        >>> res = fork_join(obs1, obs2, obs3)

    Returns:
        An operator function that takes an observable source and
        return an observable sequence containing the result
        of combining last element from each source in given sequence.
    """
    from ._forkjoin import fork_join_

    return fork_join_(*others)


def group_by(
    key_mapper: Mapper[_T, _TKey],
    element_mapper: Optional[Mapper[_T, _TValue]] = None,
    subject_mapper: Optional[Callable[[], Subject[_TValue]]] = None,
) -> Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function and comparer and selects the
    resulting elements by using a specified function.

    .. marble::
        :alt: group_by

        --1--2--a--3--b--c-|
        [    group_by()    ]
        -+-----+-----------|
               +a-----b--c-|
         +1--2-----3-------|

    Examples:
        >>> group_by(lambda x: x.id)
        >>> group_by(lambda x: x.id, lambda x: x.name)
        >>> group_by(lambda x: x.id, lambda x: x.name, lambda: ReplaySubject())

    Keyword arguments:
        key_mapper: A function to extract the key for each element.
        element_mapper: [Optional] A function to map each source
            element to an element in an observable group.
        subject_mapper: A function that returns a subject used to initiate
            a grouped observable. Default mapper returns a Subject object.

    Returns:
        An operator function that takes an observable source and
        returns a sequence of observable groups, each of which
        corresponds to a unique key value, containing all elements that
        share that same key value.
    """
    from ._groupby import group_by_

    return group_by_(key_mapper, element_mapper, subject_mapper)


def group_by_until(
    key_mapper: Mapper[_T, _TKey],
    element_mapper: Optional[Mapper[_T, _TValue]],
    duration_mapper: Callable[[GroupedObservable[_TKey, _TValue]], Observable[Any]],
    subject_mapper: Optional[Callable[[], Subject[_TValue]]] = None,
) -> Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function. A duration mapper function is used
    to control the lifetime of groups. When a group expires, it
    receives an OnCompleted notification. When a new element with the
    same key value as a reclaimed group occurs, the group will be
    reborn with a new lifetime request.

    .. marble::
        :alt: group_by_until

        --1--2--a--3--b--c-|
        [ group_by_until() ]
        -+-----+-----------|
               +a-----b--c-|
         +1--2-----3-------|

    Examples:
        >>> group_by_until(lambda x: x.id, None, lambda : reactivex.never())
        >>> group_by_until(
            lambda x: x.id, lambda x: x.name, lambda grp: reactivex.never()
        )
        >>> group_by_until(
            lambda x: x.id,
            lambda x: x.name,
            lambda grp: reactivex.never(),
            lambda: ReplaySubject()
        )

    Args:
        key_mapper: A function to extract the key for each element.
        element_mapper: A function to map each source element to an element in
            an observable group.
        duration_mapper: A function to signal the expiration of a group.
        subject_mapper: A function that returns a subject used to initiate
            a grouped observable. Default mapper returns a Subject object.

    Returns:
        An operator function that takes an observable source and
        returns a sequence of observable groups, each of which
        corresponds to a unique key value, containing all elements that
        share that same key value. If a group's lifetime expires, a new
        group with the same key value can be created once an element
        with such a key value is encountered.
    """
    from ._groupbyuntil import group_by_until_

    return group_by_until_(key_mapper, element_mapper, duration_mapper, subject_mapper)


def group_join(
    right: Observable[_TRight],
    left_duration_mapper: Callable[[_TLeft], Observable[Any]],
    right_duration_mapper: Callable[[_TRight], Observable[Any]],
) -> Callable[[Observable[_TLeft]], Observable[Tuple[_TLeft, Observable[_TRight]]]]:
    """Correlates the elements of two sequences based on overlapping
    durations, and groups the results.

    .. marble::
        :alt: group_join

        -1---2----3---4---->
        --a--------b-----c->
        [   group_join()   ]
        --a1-a2----b3-b4-c4|

    Args:
        right: The right observable sequence to join elements for.
        left_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the left observable sequence, used to determine overlap.
        right_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the right observable sequence, used to determine overlap.


    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains elements combined into
        a tuple from source elements that have an overlapping
        duration.
    """
    from ._groupjoin import group_join_

    return group_join_(right, left_duration_mapper, right_duration_mapper)


def ignore_elements() -> Callable[[Observable[_T]], Observable[_T]]:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    .. marble::
        :alt: ignore_elements

        ---1---2---3---4---|
        [ ignore_elements()]
        -------------------|

    Returns:
        An operator function that takes an observable source and
        returns an empty observable sequence that signals termination,
        successful or exceptional, of the source sequence.
    """
    from ._ignoreelements import ignore_elements_

    return ignore_elements_()


def is_empty() -> Callable[[Observable[Any]], Observable[bool]]:
    """Determines whether an observable sequence is empty.

    .. marble::
        :alt: is_empty

        -------|
        [    is_empty()    ]
        -------True-|


    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element
        determining whether the source sequence is empty.
    """
    from ._isempty import is_empty_

    return is_empty_()


def join(
    right: Observable[_T2],
    left_duration_mapper: Callable[[Any], Observable[Any]],
    right_duration_mapper: Callable[[Any], Observable[Any]],
) -> Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]:
    """Correlates the elements of two sequences based on overlapping
    durations.

    .. marble::
        :alt: join

        -1---2----3---4---->
        --a--------b-----c->
        [       join()     ]
        --a1-a2----b3-b4-c4|

    Args:
        right: The right observable sequence to join elements for.
        left_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the left observable sequence, used to determine overlap.
        right_duration_mapper: A function to select the duration
            (expressed as an observable sequence) of each element of
            the right observable sequence, used to determine overlap.

    Return:
        An operator function that takes an observable source and
        returns an observable sequence that contains elements combined
        into a tuple from source elements that have an overlapping
        duration.
    """
    from ._join import join_

    return join_(right, left_duration_mapper, right_duration_mapper)


def last(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The last operator.

    Returns the last element of an observable sequence that satisfies
    the condition in the predicate if specified, else the last element.

    .. marble::
        :alt: last

        ---1--2--3--4-|
        [      last()      ]
        ------------4-|

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
    from ._last import last_

    return last_(predicate)


@overload
def last_or_default() -> Callable[[Observable[_T]], Observable[Optional[_T]]]:
    ...


@overload
def last_or_default(
    default_value: _T,
) -> Callable[[Observable[_T]], Observable[_T]]:
    ...


@overload
def last_or_default(
    default_value: _T,
    predicate: Predicate[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    ...


def last_or_default(
    default_value: Any = None,
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[Any]]:
    """The last_or_default operator.

    Returns the last element of an observable sequence that satisfies
    the condition in the predicate, or a default value if no such
    element exists.

    .. marble::
        :alt: last

        ---1--2--3--4-|
        [last_or_default(8)]
        --------------8-|


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
    from ._lastordefault import last_or_default

    return last_or_default(default_value, predicate)


def map(
    mapper: Optional[Mapper[_T1, _T2]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    """The map operator.

    Project each element of an observable sequence into a new form.

    .. marble::
        :alt: map

        ---1---2---3---4--->
        [   map(i: i*2)    ]
        ---2---4---6---8--->


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
    from ._map import map_

    return map_(mapper)


def map_indexed(
    mapper_indexed: Optional[MapperIndexed[_T1, _T2]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    .. marble::
        :alt: map_indexed

        ---1---2---3---4--->
        [  map(i,id: i*2)  ]
        ---2---4---6---8--->

    Example:
        >>> ret = map_indexed(lambda value, index: value * value + index)

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
    from ._map import map_indexed_

    return map_indexed_(mapper_indexed)


def materialize() -> Callable[[Observable[_T]], Observable[Notification[_T]]]:
    """Materializes the implicit notifications of an observable
    sequence as explicit notification values.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the materialized
        notification values from the source sequence.
    """
    from ._materialize import materialize

    return materialize()


def max(
    comparer: Optional[Comparer[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the maximum value in an observable sequence according to
    the specified comparer.

    .. marble::
        :alt: max

        ---1--2--3--4-|
        [      max()       ]
        --------------4-|

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
    from ._max import max_

    return max_(comparer)


def max_by(
    key_mapper: Mapper[_T, _TKey], comparer: Optional[Comparer[_TKey]] = None
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """The max_by operator.

    Returns the elements in an observable sequence with the maximum
    key value according to the specified comparer.

    .. marble::
        :alt: max_by

        ---1--2--3--4-|
        [     max_by()     ]
        --------------4-|

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
    from ._maxby import max_by_

    return max_by_(key_mapper, comparer)


def merge(
    *sources: Observable[Any], max_concurrent: Optional[int] = None
) -> Callable[[Observable[Any]], Observable[Any]]:
    """Merges an observable sequence of observable sequences into an
    observable sequence, limiting the number of concurrent
    subscriptions to inner sequences. Or merges two observable
    sequences into a single observable sequence.

    .. marble::
        :alt: merge

        ---1---2---3---4-|
        -a---b---c---d--|
        [     merge()      ]
        -a-1-b-2-c-3-d-4-|

    Examples:
        >>> op = merge(max_concurrent=1)
        >>> op = merge(other_source)

    Args:
        max_concurrent: [Optional] Maximum number of inner observable
            sequences being subscribed to concurrently or the second
            observable sequence.

    Returns:
        An operator function that takes an observable source and
        returns the observable sequence that merges the elements of the
        inner sequences.
    """
    from ._merge import merge_

    return merge_(*sources, max_concurrent=max_concurrent)


def merge_all() -> Callable[[Observable[Observable[_T]]], Observable[_T]]:
    """The merge_all operator.

    Merges an observable sequence of observable sequences into an
    observable sequence.

    .. marble::
        :alt: merge_all

        ---1---2---3---4-|
        -a---b---c---d--|
        [   merge_all()    ]
        -a-1-b-2-c-3-d-4-|

    Returns:
        A partially applied operator function that takes an observable
        source and returns the observable sequence that merges the
        elements of the inner sequences.
    """
    from ._merge import merge_all_

    return merge_all_()


def min(
    comparer: Optional[Comparer[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The `min` operator.

    Returns the minimum element in an observable sequence according to
    the optional comparer else a default greater than less than check.

    .. marble::
        :alt: min

        ---1--2--3--4-|
        [      min()       ]
        --------------1-|

    Examples:
        >>> res = source.min()
        >>> res = source.min(lambda x, y: x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element
        with the minimum element in the source sequence.
    """
    from ._min import min_

    return min_(comparer)


def min_by(
    key_mapper: Mapper[_T, _TKey], comparer: Optional[Comparer[_TKey]] = None
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """The `min_by` operator.

    Returns the elements in an observable sequence with the minimum key
    value according to the specified comparer.

    .. marble::
        :alt: min_by

        ---1--2--3--4-|
        [     min_by()     ]
        --------------1-|

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
    from ._minby import min_by_

    return min_by_(key_mapper, comparer)


@overload
def multicast() -> Callable[[Observable[_T]], ConnectableObservable[_T]]:
    ...


@overload
def multicast(
    subject: abc.SubjectBase[_T],
) -> Callable[[Observable[_T]], ConnectableObservable[_T]]:
    ...


@overload
def multicast(
    *,
    subject_factory: Callable[[Optional[abc.SchedulerBase]], abc.SubjectBase[_T]],
    mapper: Optional[Callable[[Observable[_T]], Observable[_T2]]] = None,
) -> Callable[[Observable[_T]], Observable[_T2]]:
    ...


def multicast(
    subject: Optional[abc.SubjectBase[_T]] = None,
    *,
    subject_factory: Optional[
        Callable[[Optional[abc.SchedulerBase]], abc.SubjectBase[_T]]
    ] = None,
    mapper: Optional[Callable[[Observable[_T]], Observable[_T2]]] = None,
) -> Callable[[Observable[_T]], Union[Observable[_T2], ConnectableObservable[_T]]]:
    """Multicasts the source sequence notifications through an
    instantiated subject into all uses of the sequence within a mapper
    function. Each subscription to the resulting sequence causes a
    separate multicast invocation, exposing the sequence resulting from
    the mapper function's invocation. For specializations with fixed
    subject types, see Publish, PublishLast, and Replay.

    Examples:
        >>> res = multicast(observable)
        >>> res = multicast(
            subject_factory=lambda scheduler: Subject(), mapper=lambda x: x
        )

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
    from ._multicast import multicast_

    return multicast_(subject, subject_factory=subject_factory, mapper=mapper)


def observe_on(
    scheduler: abc.SchedulerBase,
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._observeon import observe_on_

    return observe_on_(scheduler)


def on_error_resume_next(
    second: Observable[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Continues an observable sequence that is terminated normally
    or by an exception with the next observable sequence.

    .. marble::
        :alt: on_error

        ---1--2--3--4-*
             e-a--b-|
        [   on_error(e)    ]
        -1--2--3--4-a--b-|

    Keyword arguments:
        second: Second observable sequence used to produce results
            after the first sequence terminates.


    Returns:
        An observable sequence that concatenates the first and
        second sequence, even if the first sequence terminates
        exceptionally.
    """

    from ._onerrorresumenext import on_error_resume_next_

    return on_error_resume_next_(second)


def pairwise() -> Callable[[Observable[_T]], Observable[Tuple[_T, _T]]]:
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
    from ._pairwise import pairwise_

    return pairwise_()


def partition(
    predicate: Predicate[_T],
) -> Callable[[Observable[_T]], List[Observable[_T]]]:
    """Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations
    for those values for which the predicate returns true. The second
    will trigger observations for those values where the predicate
    returns false. The predicate is executed once for each subscribed
    observer. Both also propagate all error observations arising from
    the source and each completes when the source completes.

    .. marble::
        :alt: partition

        ---1--2--3--4--|
        [ partition(even)  ]
        ---1-----3-----|
        ------2-----4--|

    Args:
        predicate: The function to determine which output Observable
        will trigger a particular observation.

    Returns:
        An operator function that takes an observable source and
        returns a list of observables. The first triggers when the
        predicate returns True, and the second triggers when the
        predicate returns False.
    """
    from ._partition import partition_

    return partition_(predicate)


def partition_indexed(
    predicate_indexed: PredicateIndexed[_T],
) -> Callable[[Observable[_T]], List[Observable[_T]]]:
    """The indexed partition operator.

    Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations
    for those values for which the predicate returns true. The second
    will trigger observations for those values where the predicate
    returns false. The predicate is executed once for each subscribed
    observer. Both also propagate all error observations arising from
    the source and each completes when the source completes.

    .. marble::
        :alt: partition_indexed

        ---1--2--3--4--|
        [ partition(even)  ]
        ---1-----3-----|
        ------2-----4--|

    Args:
        predicate: The function to determine which output Observable
        will trigger a particular observation.

    Returns:
        A list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate
        returns False.
    """
    from ._partition import partition_indexed_

    return partition_indexed_(predicate_indexed)


def pluck(
    key: _TKey,
) -> Callable[[Observable[Dict[_TKey, _TValue]]], Observable[_TValue]]:
    """Retrieves the value of a specified key using dict-like access (as in
    element[key]) from all elements in the Observable sequence.

    To pluck an attribute of each element, use pluck_attr.

    Args:
        key: The key to pluck.

    Returns:
        An operator function that takes an observable source and
        returns a new observable sequence of key values.
    """
    from ._pluck import pluck_

    return pluck_(key)


def pluck_attr(prop: str) -> Callable[[Observable[Any]], Observable[Any]]:
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
    from ._pluck import pluck_attr_

    return pluck_attr_(prop)


@overload
def publish() -> Callable[[Observable[_T1]], ConnectableObservable[_T1]]:
    ...


@overload
def publish(
    mapper: Mapper[Observable[_T1], Observable[_T2]],
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


def publish(
    mapper: Optional[Mapper[Observable[_T1], Observable[_T2]]] = None,
) -> Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]:
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
    from ._publish import publish_

    return publish_(mapper)


@overload
def publish_value(
    initial_value: _T1,
) -> Callable[[Observable[_T1]], ConnectableObservable[_T1]]:
    ...


@overload
def publish_value(
    initial_value: _T1,
    mapper: Mapper[Observable[_T1], Observable[_T2]],
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


def publish_value(
    initial_value: _T1,
    mapper: Optional[Mapper[Observable[_T1], Observable[_T2]]] = None,
) -> Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]:
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
        An operator function that takes an observable source and returns
        an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from ._publishvalue import publish_value_

    return publish_value_(initial_value, mapper)


@overload
def reduce(
    accumulator: Accumulator[_TState, _T]
) -> Callable[[Observable[_T]], Observable[_T]]:
    ...


@overload
def reduce(
    accumulator: Accumulator[_TState, _T], seed: _TState
) -> Callable[[Observable[_T]], Observable[_TState]]:
    ...


def reduce(
    accumulator: Accumulator[_TState, _T], seed: Union[_TState, Type[NotSet]] = NotSet
) -> Callable[[Observable[_T]], Observable[Any]]:
    """The reduce operator.

    Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results,
    see `scan`.

    .. marble::
        :alt: reduce

        ---1--2--3--4--|
        [reduce(acc,i: acc+i)]
        ---------------10-|

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
    from ._reduce import reduce_

    return reduce_(accumulator, seed)


def ref_count() -> Callable[[ConnectableObservable[_T]], Observable[_T]]:
    """Returns an observable sequence that stays connected to the
    source as long as there is at least one subscription to the
    observable sequence.
    """
    from .connectable._refcount import ref_count_

    return ref_count_()


def repeat(
    repeat_count: Optional[int] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Repeats the observable sequence a specified number of times.
    If the repeat count is not specified, the sequence repeats
    indefinitely.

    .. marble::
        :alt: repeat

        -1--2-|
        [    repeat(3)     ]
        -1--2--1--2--1--2-|


    Examples:
        >>> repeated = repeat()
        >>> repeated = repeat(42)
    Args:
        repeat_count: Number of times to repeat the sequence. If not
        provided, repeats the sequence indefinitely.

    Returns:
        An operator function that takes an observable sources and
        returns an observable sequence producing the elements of the
        given sequence repeatedly.
    """
    from ._repeat import repeat_

    return repeat_(repeat_count)


@overload
def replay(
    buffer_size: Optional[int] = None,
    window: Optional[typing.RelativeTime] = None,
    *,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T1]], ConnectableObservable[_T1]]:
    ...


@overload
def replay(
    buffer_size: Optional[int] = None,
    window: Optional[typing.RelativeTime] = None,
    *,
    mapper: Optional[Mapper[Observable[_T1], Observable[_T2]]],
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    ...


def replay(
    buffer_size: Optional[int] = None,
    window: Optional[typing.RelativeTime] = None,
    *,
    mapper: Optional[Mapper[Observable[_T1], Observable[_T2]]] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T1]], Union[Observable[_T2], ConnectableObservable[_T1]]]:
    """The `replay` operator.

    Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence replaying notifications
    subject to a maximum time length for the replay buffer.

    This operator is a specialization of Multicast using a
    ReplaySubject.

    Examples:
        >>> res = replay(buffer_size=3)
        >>> res = replay(buffer_size=3, window=0.5)
        >>> res = replay(None, 3, 0.5)
        >>> res = replay(lambda x: x.take(6).repeat(), 3, 0.5)

    Args:
        mapper: [Optional] Selector function which can use the
            multicasted source sequence as many times as needed,
            without causing multiple subscriptions to the source
            sequence. Subscribers to the given source will receive all
            the notifications of the source subject to the specified
            replay buffer trimming policy.
        buffer_size: [Optional] Maximum element count of the replay
            buffer.
        window: [Optional] Maximum time length of the replay buffer.
        scheduler: [Optional] Scheduler the observers are invoked on.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """
    from ._replay import replay_

    return replay_(mapper, buffer_size, window, scheduler=scheduler)


def retry(
    retry_count: Optional[int] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._retry import retry_

    return retry_(retry_count)


def sample(
    sampler: Union[typing.RelativeTime, Observable[Any]],
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Samples the observable sequence at each interval.

    .. marble::
        :alt: sample

        ---1-2-3-4------|
        [   sample(4)   ]
        ----1---3---4---|

    Examples:
        >>> res = sample(sample_observable) # Sampler tick sequence
        >>> res = sample(5.0) # 5 seconds

    Args:
        sampler: Observable used to sample the source observable **or** time
            interval at which to sample (specified as a float denoting
            seconds or an instance of timedelta).
        scheduler: Scheduler to use only when a time interval is given.

    Returns:
        An operator function that takes an observable source and
        returns a sampled observable sequence.
    """
    from ._sample import sample_

    return sample_(sampler, scheduler)


@overload
def scan(
    accumulator: Accumulator[_T, _T]
) -> Callable[[Observable[_T]], Observable[_T]]:
    ...


@overload
def scan(
    accumulator: Accumulator[_TState, _T], seed: Union[_TState, Type[NotSet]]
) -> Callable[[Observable[_T]], Observable[_TState]]:
    ...


def scan(
    accumulator: Accumulator[_TState, _T], seed: Union[_TState, Type[NotSet]] = NotSet
) -> Callable[[Observable[_T]], Observable[_TState]]:
    """The scan operator.

    Applies an accumulator function over an observable sequence and
    returns each intermediate result. The optional seed value is used
    as the initial accumulator value. For aggregation behavior with no
    intermediate results, see `aggregate()` or `Observable()`.

    .. marble::
        :alt: scan

        ----1--2--3--4-----|
        [scan(acc,i: acc+i)]
        ----1--3--6--10----|

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
    from ._scan import scan_

    return scan_(accumulator, seed)


def sequence_equal(
    second: Union[Observable[_T], Iterable[_T]], comparer: Optional[Comparer[_T]] = None
) -> Callable[[Observable[_T]], Observable[bool]]:
    """Determines whether two sequences are equal by comparing the
    elements pairwise using a specified equality comparer.

    .. marble::
        :alt: scan

        -1--2--3--4----|
        ----1--2--3--4-|
        [ sequence_equal() ]
        ---------------True|

    Examples:
        >>> res = sequence_equal([1,2,3])
        >>> res = sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
        >>> res = sequence_equal(reactivex.return_value(42))
        >>> res = sequence_equal(
            reactivex.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

    Args:
        second: Second observable sequence or iterable to compare.
        comparer: [Optional] Comparer used to compare elements of both
            sequences. No guarantees on order of comparer arguments.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains a single element
        which indicates whether both sequences are of equal length and
        their corresponding elements are equal according to the
        specified equality comparer.
    """
    from ._sequenceequal import sequence_equal_

    return sequence_equal_(second, comparer)


def share() -> Callable[[Observable[_T]], Observable[_T]]:
    """Share a single subscription among multiple observers.

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
    from ._publish import share_

    return share_()


def single(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The single operator.

    Returns the only element of an observable sequence that satisfies
    the condition in the optional predicate, and reports an exception
    if there is not exactly one element in the observable sequence.

    .. marble::
        :alt: single

        ----1--2--3--4-----|
        [     single(3)    ]
        ----------3--------|

    Example:
        >>> res = single()
        >>> res = single(lambda x: x == 42)

    Args:
        predicate: [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the single element in
        the observable sequence that satisfies the condition in the
        predicate.
    """
    from ._single import single_

    return single_(predicate)


def single_or_default(
    predicate: Optional[Predicate[_T]] = None, default_value: Any = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the only element of an observable sequence that matches
    the predicate, or a default value if no such element exists this
    method reports an exception if there is more than one element in
    the observable sequence.

    .. marble::
        :alt: single_or_default

        ----1--2--3--4--|
        [    single(8,42)  ]
        ----------------42-|

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
        An operator function that takes an observable source and
        returns an observable sequence containing the single element in
        the observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
    """
    from ._singleordefault import single_or_default_

    return single_or_default_(predicate, default_value)


def single_or_default_async(
    has_default: bool = False, default_value: _T = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    from ._singleordefault import single_or_default_async_

    return single_or_default_async_(has_default, default_value)


def skip(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    """The skip operator.

    Bypasses a specified number of elements in an observable sequence
    and then returns the remaining elements.

    .. marble::
        :alt: skip

        ----1--2--3--4-----|
        [     skip(2)      ]
        ----------3--4-----|


    Args:
        count: The number of elements to skip before returning the
            remaining elements.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements that
        occur after the specified index in the input sequence.
    """
    from ._skip import skip_

    return skip_(count)


def skip_last(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    """The skip_last operator.

    .. marble::
        :alt: skip_last

        ----1--2--3--4-----|
        [   skip_last(1)   ]
        -------1--2--3-----|


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
    from ._skiplast import skip_last_

    return skip_last_(count)


def skip_last_with_time(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Skips elements for the specified duration from the end of the
    observable source sequence.

    Example:
        >>> res = skip_last_with_time(5.0)

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
    from ._skiplastwithtime import skip_last_with_time_

    return skip_last_with_time_(duration, scheduler=scheduler)


def skip_until(
    other: Union[Observable[Any], "Future[Any]"]
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the values from the source observable sequence only
    after the other observable sequence produces a value.

    .. marble::
        :alt: skip_until

        ----1--2--3--4-----|
        ---------1---------|
        [   skip_until()   ]
        ----------3--4-----|

    Args:
        other: The observable sequence that triggers propagation of
            elements of the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the elements of the
        source sequence starting from the point the other sequence
        triggered propagation.
    """
    from ._skipuntil import skip_until_

    return skip_until_(other)


def skip_until_with_time(
    start_time: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Skips elements from the observable source sequence until the
    specified start time.
    Errors produced by the source sequence are always forwarded to the
    result sequence, even if the error occurs before the start time.

    .. marble::
        :alt: skip_until

        ------1--2--3--4-------|
        [skip_until_with_time()]
        ------------3--4-------|

    Examples:
        >>> res = skip_until_with_time(datetime())
        >>> res = skip_until_with_time(5.0)

    Args:
        start_time: Time to start taking elements from the source
            sequence. If this value is less than or equal to
            `datetime.utcnow()`, no elements will be skipped.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with the elements skipped
        until the specified start time.
    """
    from ._skipuntilwithtime import skip_until_with_time_

    return skip_until_with_time_(start_time, scheduler=scheduler)


def skip_while(
    predicate: typing.Predicate[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The `skip_while` operator.

    Bypasses elements in an observable sequence as long as a specified
    condition is true and then returns the remaining elements. The
    element's index is used in the logic of the predicate function.

    .. marble::
        :alt: skip_while

        ----1--2--3--4-----|
        [skip_while(i: i<3)]
        ----------3--4-----|

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
    from ._skipwhile import skip_while_

    return skip_while_(predicate)


def skip_while_indexed(
    predicate: typing.PredicateIndexed[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Bypasses elements in an observable sequence as long as a
    specified condition is true and then returns the remaining
    elements. The element's index is used in the logic of the predicate
    function.

    .. marble::
        :alt: skip_while_indexed

        ----1--2--3--4-----|
        [skip_while(i: i<3)]
        ----------3--4-----|

    Example:
        >>> skip_while(lambda value, index: value < 10 or index < 10)

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
    from ._skipwhile import skip_while_indexed_

    return skip_while_indexed_(predicate)


def skip_with_time(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Skips elements for the specified duration from the start of the
    observable source sequence.

    .. marble::
        :alt: skip_with_time

        ----1--2--3--4-----|
        [ skip_with_time() ]
        ----------3--4-----|

    Args:
        >>> res = skip_with_time(5.0)

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
    from ._skipwithtime import skip_with_time_

    return skip_with_time_(duration, scheduler=scheduler)


def slice(
    start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """The slice operator.

    Slices the given observable. It is basically a wrapper around the operators
    :func:`skip <reactivex.operators.skip>`,
    :func:`skip_last <reactivex.operators.skip_last>`,
    :func:`take <reactivex.operators.take>`,
    :func:`take_last <reactivex.operators.take_last>` and
    :func:`filter <reactivex.operators.filter>`.

    .. marble::
        :alt: slice

        ----1--2--3--4-----|
        [   slice(1, 2)    ]
        -------2--3--------|

    Examples:
        >>> result = source.slice(1, 10)
        >>> result = source.slice(1, -2)
        >>> result = source.slice(1, -1, 2)

    Args:
        start: First element to take of skip last
        stop: Last element to take of skip last
        step: Takes every step element. Must be larger than zero

    Returns:
        An operator function that takes an observable source and
        returns a sliced observable sequence.
    """
    from ._slice import slice_

    return slice_(start, stop, step)


def some(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[bool]]:
    """The some operator.

    Determines whether some element of an observable sequence
    satisfies a condition if present, else if some items are in the
    sequence.

    .. marble::
        :alt: some

        ----1--2--3--4-----|
        [   some(i: i>3)   ]
        -------------True--|

    Examples:
        >>> result = source.some()
        >>> result = source.some(lambda x: x > 3)

    Args:
        predicate: A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing a single element
        determining whether some elements in the source sequence
        pass the test in the specified predicate if given, else if some
        items are in the sequence.
    """
    from ._some import some_

    return some_(predicate)


@overload
def starmap(
    mapper: Callable[[_A, _B], _T]
) -> Callable[[Observable[Tuple[_A, _B]]], Observable[_T]]:
    ...


@overload
def starmap(
    mapper: Callable[[_A, _B, _C], _T]
) -> Callable[[Observable[Tuple[_A, _B, _C]]], Observable[_T]]:
    ...


@overload
def starmap(
    mapper: Callable[[_A, _B, _C, _D], _T]
) -> Callable[[Observable[Tuple[_A, _B, _C, _D]]], Observable[_T]]:
    ...


def starmap(
    mapper: Optional[Callable[..., Any]] = None
) -> Callable[[Observable[Any]], Observable[Any]]:
    """The starmap operator.

    Unpack arguments grouped as tuple elements of an observable
    sequence and return an observable sequence of values by invoking
    the mapper function with star applied unpacked elements as
    positional arguments.

    Use instead of `map()` when the the arguments to the mapper is
    grouped as tuples and the mapper function takes multiple arguments.

    .. marble::
        :alt: starmap

        -----1,2---3,4-----|
        [   starmap(add)   ]
        -----3-----7-------|

    Example:
        >>> starmap(lambda x, y: x + y)

    Args:
        mapper: A transform function to invoke with unpacked elements
            as arguments.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the results of
        invoking the mapper function with unpacked elements of the
        source.
    """

    if mapper is None:
        return compose(identity)

    def starred(values: Tuple[Any, ...]) -> Any:
        assert mapper  # mypy is paranoid
        return mapper(*values)

    return compose(map(starred))


@overload
def starmap_indexed(
    mapper: Callable[[_A, int], _T]
) -> Callable[[Observable[_A]], Observable[_T]]:
    ...


@overload
def starmap_indexed(
    mapper: Callable[[_A, _B, int], _T]
) -> Callable[[Observable[Tuple[_A, _B]]], Observable[_T]]:
    ...


@overload
def starmap_indexed(
    mapper: Callable[[_A, _B, _C, int], _T]
) -> Callable[[Observable[Tuple[_A, _B, _C]]], Observable[_T]]:
    ...


@overload
def starmap_indexed(
    mapper: Callable[[_A, _B, _C, _D, int], _T]
) -> Callable[[Observable[Tuple[_A, _B, _C, _D]]], Observable[_T]]:
    ...


def starmap_indexed(
    mapper: Optional[Callable[..., Any]] = None
) -> Callable[[Observable[Any]], Observable[Any]]:
    """Variant of :func:`starmap` which accepts an indexed mapper.

    .. marble::
        :alt: starmap_indexed

        ---------1,2---3,4---------|
        [   starmap_indexed(sum)   ]
        ---------3-----8-----------|

    Example:
        >>> starmap_indexed(lambda x, y, i: x + y + i)

    Args:
        mapper: A transform function to invoke with unpacked elements
            as arguments.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the results of
        invoking the indexed mapper function with unpacked elements
        of the source.
    """
    from ._map import map_

    if mapper is None:
        return compose(identity)

    def starred(values: Tuple[Any, ...]) -> Any:
        assert mapper  # mypy is paranoid
        return mapper(*values)

    return compose(map_(starred))


def start_with(*args: _T) -> Callable[[Observable[_T]], Observable[_T]]:
    """Prepends a sequence of values to an observable sequence.

    .. marble::
        :alt: start_with

        -----1--2--3--4----|
        [  start_with(7,8) ]
        -7-8-1--2--3--4----|

    Example:
        >>> start_with(1, 2, 3)

    Returns:
        An operator function that takes a source observable and returns
        the source sequence prepended with the specified values.
    """
    from ._startswith import start_with_

    return start_with_(*args)


def subscribe_on(
    scheduler: abc.SchedulerBase,
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._subscribeon import subscribe_on_

    return subscribe_on_(scheduler)


@overload
def sum() -> Callable[[Observable[float]], Observable[float]]:
    ...


@overload
def sum(key_mapper: Mapper[_T, float]) -> Callable[[Observable[_T]], Observable[float]]:
    ...


def sum(
    key_mapper: Optional[Mapper[Any, float]] = None
) -> Callable[[Observable[Any]], Observable[float]]:
    """Computes the sum of a sequence of values that are obtained by
    invoking an optional transform function on each element of the
    input sequence, else if not specified computes the sum on each item
    in the sequence.

    .. marble::
        :alt: sum

        -----1--2--3--4-|
        [       sum()      ]
        ----------------10-|

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
    from ._sum import sum_

    return sum_(key_mapper)


def switch_latest() -> Callable[
    [Observable[Union[Observable[_T], "Future[_T]"]]], Observable[_T]
]:
    """The switch_latest operator.

    Transforms an observable sequence of observable sequences into an
    observable sequence producing values only from the most recent
    observable sequence.

    .. marble::
        :alt: switch_latest

        -+------+----------|
                +--a--b--c-|
         +--1--2--3--4--|
        [ switch_latest()  ]
        ----1--2---a--b--c-|

    Returns:
        A partially applied operator function that takes an observable
        source and returns the observable sequence that at any point in
        time produces the elements of the most recent inner observable
        sequence that has been received.
    """
    from ._switchlatest import switch_latest_

    return switch_latest_()


def take(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns a specified number of contiguous elements from the start
    of an observable sequence.

    .. marble::
        :alt: take

        -----1--2--3--4----|
        [    take(2)       ]
        -----1--2-|

    Example:
        >>> op = take(5)

    Args:
        count: The number of elements to return.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the specified
        number of elements from the start of the input sequence.
    """
    from ._take import take_

    return take_(count)


def take_last(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns a specified number of contiguous elements from the end
    of an observable sequence.

    .. marble::
        :alt: take_last

        -1--2--3--4-|
        [  take_last(2)    ]
        ------------3--4-|

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
    from ._takelast import take_last_

    return take_last_(count)


def take_last_buffer(count: int) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """The `take_last_buffer` operator.

    Returns an array with the specified number of contiguous elements
    from the end of an observable sequence.

    .. marble::
        :alt: take_last_buffer

        -----1--2--3--4-|
        [take_last_buffer(2)]
        ----------------3,4-|

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
    from ._takelastbuffer import take_last_buffer_

    return take_last_buffer_(count)


def take_last_with_time(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns elements within the specified duration from the end of
    the observable source sequence.

    .. marble::
        :alt: take_last_with_time

        -----1--2--3--4-|
        [take_last_with_time(3)]
        ----------------4-|

    Example:
        >>> res = take_last_with_time(5.0)

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
    from ._takelastwithtime import take_last_with_time_

    return take_last_with_time_(duration, scheduler=scheduler)


def take_until(other: Observable[Any]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the values from the source observable sequence until the
    other observable sequence produces a value.

    .. marble::
        :alt: take_until

        -----1--2--3--4----|
        -------------a-|
        [   take_until(2)  ]
        -----1--2--3-------|

    Args:
        other: Observable sequence that terminates propagation of
            elements of the source sequence.

    Returns:
        An operator function that takes an observable source and
        returns as observable sequence containing the elements of the
        source sequence up to the point the other sequence interrupted
        further propagation.
    """
    from ._takeuntil import take_until_

    return take_until_(other)


def take_until_with_time(
    end_time: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Takes elements for the specified duration until the specified
    end time, using the specified scheduler to run timers.

    .. marble::
        :alt: take_until_with_time

        -----1--2--3--4--------|
        [take_until_with_time()]
        -----1--2--3-----------|

    Examples:
        >>> res = take_until_with_time(dt, [optional scheduler])
        >>> res = take_until_with_time(5.0, [optional scheduler])

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
    from ._takeuntilwithtime import take_until_with_time_

    return take_until_with_time_(end_time, scheduler=scheduler)


def take_while(
    predicate: Predicate[_T], inclusive: bool = False
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns elements from an observable sequence as long as a
    specified condition is true.

    .. marble::
        :alt: take_while

        -----1--2--3--4----|
        [take_while(i: i<3)]
        -----1--2----------|

    Example:
        >>> take_while(lambda value: value < 10)

    Args:
        predicate: A function to test each element for a condition.
        inclusive: [Optional]  When set to True the value that caused
            the predicate function to return False will also be emitted.
            If not specified, defaults to False.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence that contains the elements from
        the input sequence that occur before the element at which the
        test no longer passes.
    """
    from ._takewhile import take_while_

    return take_while_(predicate, inclusive)


def take_while_indexed(
    predicate: PredicateIndexed[_T], inclusive: bool = False
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns elements from an observable sequence as long as a
    specified condition is true. The element's index is used in the
    logic of the predicate function.

    .. marble::
        :alt: take_while_indexed

        --------1------2------3------4-------|
        [take_while_indexed(v, i: v<4 or i<3)]
        --------1------2---------------------|

    Example:
        >>> take_while_indexed(lambda value, index: value < 10 or index < 10)

    Args:
        predicate: A function to test each element for a condition; the
            second parameter of the function represents the index of the
            source element.
        inclusive: [Optional]  When set to True the value that caused
            the predicate function to return False will also be emitted.
            If not specified, defaults to False.

    Returns:
        An observable sequence that contains the elements from the
        input sequence that occur before the element at which the test no
        longer passes.
    """
    from ._takewhile import take_while_indexed_

    return take_while_indexed_(predicate, inclusive)


def take_with_time(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Takes elements for the specified duration from the start of the
    observable source sequence.

    .. marble::
        :alt: take_with_time

        -----1--2--3--4----|
        [ take_with_time() ]
        -----1--2----------|

    Example:
        >>> res = take_with_time(5.0)

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
    from ._takewithtime import take_with_time_

    return take_with_time_(duration, scheduler=scheduler)


def throttle_first(
    window_duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._throttlefirst import throttle_first_

    return throttle_first_(window_duration, scheduler)


def throttle_with_mapper(
    throttle_duration_mapper: Callable[[Any], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._debounce import throttle_with_mapper_

    return throttle_with_mapper_(throttle_duration_mapper)


if TYPE_CHECKING:
    from ._timestamp import Timestamp


def timestamp(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable["Timestamp[_T]"]]:
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
    from ._timestamp import timestamp_

    return timestamp_(scheduler=scheduler)


def timeout(
    duetime: typing.AbsoluteOrRelativeTime,
    other: Optional[Observable[_T]] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the source observable sequence or the other observable
    sequence if duetime elapses.

    .. marble::
        :alt: timeout

        -1--2--------3--4--|
           o-6--7-|
        [   timeout(3,o)      ]
        -1--2---6--7----------|

    Examples:
        >>> res = timeout(5.0)
        >>> res = timeout(datetime(), return_value(42))
        >>> res = timeout(5.0, return_value(42))

    Args:
        duetime: Absolute (specified as a datetime object) or relative time
            (specified as a float denoting seconds or an instance of timedetla)
            when a timeout occurs.
        other: Sequence to return in case of a timeout. If not
            specified, a timeout error throwing sequence will be used.
        scheduler:

    Returns:
        An operator function that takes and observable source and
        returns the source sequence switching to the other sequence in
        case of a timeout.
    """
    from ._timeout import timeout_

    return timeout_(duetime, other, scheduler)


def timeout_with_mapper(
    first_timeout: Optional[Observable[Any]] = None,
    timeout_duration_mapper: Optional[Callable[[_T], Observable[Any]]] = None,
    other: Optional[Observable[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the source observable sequence, switching to the other
    observable sequence if a timeout is signaled.

    Examples:
        >>> res = timeout_with_mapper(reactivex.timer(0.5))
        >>> res = timeout_with_mapper(
            reactivex.timer(0.5), lambda x: reactivex.timer(0.2)
        )
        >>> res = timeout_with_mapper(
            reactivex.timer(0.5),
            lambda x: reactivex.timer(0.2),
            reactivex.return_value(42)
        )

    Args:
        first_timeout: [Optional] Observable sequence that represents
            the timeout for the first element. If not provided, this
            defaults to reactivex.never().
        timeout_duration_mapper: [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the
            current element and the next element.
        other: [Optional] Sequence to return in case of a timeout. If
            not provided, this is set to reactivex.throw().

    Returns:
        An operator function that takes an observable source and
        returns the source sequence switching to the other sequence in
        case of a timeout.
    """
    from ._timeoutwithmapper import timeout_with_mapper_

    return timeout_with_mapper_(first_timeout, timeout_duration_mapper, other)


if TYPE_CHECKING:
    from ._timeinterval import TimeInterval


def time_interval(
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable["TimeInterval[_T]"]]:
    """Records the time interval between consecutive values in an
    observable sequence.

    .. marble::
        :alt: time_interval

        --1--2-----3---4--|
        [ time_interval()  ]
        -----2-----5---5---|

    Examples:
        >>> res = time_interval()

    Return:
        An operator function that takes an observable source and
        returns an observable sequence with time interval information
        on values.
    """
    from ._timeinterval import time_interval_

    return time_interval_(scheduler=scheduler)


def to_dict(
    key_mapper: Mapper[_T, _TKey], element_mapper: Optional[Mapper[_T, _TValue]] = None
) -> Callable[[Observable[_T]], Observable[Dict[_TKey, _TValue]]]:
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
    from ._todict import to_dict_

    return to_dict_(key_mapper, element_mapper)


def to_future(
    future_ctor: Optional[Callable[[], "Future[_T]"]] = None
) -> Callable[[Observable[_T]], "Future[_T]"]:
    """Converts an existing observable sequence to a Future.

    Example:
        op = to_future(asyncio.Future);

    Args:
        future_ctor: [Optional] The constructor of the future.

    Returns:
        An operator function that takes an observable source and returns
        a future with the last value from the observable sequence.
    """
    from ._tofuture import to_future_

    return to_future_(future_ctor)


def to_iterable() -> Callable[[Observable[_T]], Observable[List[_T]]]:
    """Creates an iterable from an observable sequence.

    There is also an alias called ``to_list``.

    Returns:
        An operator function that takes an obserable source and
        returns an observable sequence containing a single element with
        an iterable containing all the elements of the source sequence.
    """
    from ._toiterable import to_iterable_

    return to_iterable_()


to_list = to_iterable


def to_marbles(
    timespan: typing.RelativeTime = 0.1, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[Any]], Observable[str]]:
    """Convert an observable sequence into a marble diagram string.

    Args:
        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Observable stream.
    """
    from ._tomarbles import to_marbles

    return to_marbles(scheduler=scheduler, timespan=timespan)


def to_set() -> Callable[[Observable[_T]], Observable[Set[_T]]]:
    """Converts the observable sequence to a set.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with a single value of a set
        containing the values from the observable sequence.
    """
    from ._toset import to_set_

    return to_set_()


def while_do(
    condition: Predicate[Observable[_T]],
) -> Callable[[Observable[_T]], Observable[_T]]:
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
    from ._whiledo import while_do_

    return while_do_(condition)


def window(
    boundaries: Observable[Any],
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    .. marble::
        :alt: window

        ---a-----b-----c--------|
        ----1--2--3--4--5--6--7-|
        [ window(open)          ]
        +--+-----+-----+--------|
                       +5--6--7-|
                 +3--4-|
           +1--2-|
        +--|

    Examples:
        >>> res = window(reactivex.interval(1.0))

    Args:
        boundaries: Observable sequence whose elements denote the
            creation and completion of non-overlapping windows.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of windows.

    """
    from ._window import window_

    return window_(boundaries)


def window_when(
    closing_mapper: Callable[[], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    .. marble::
        :alt: window

        ------c|
              ------c|
                    ------c|
        ----1--2--3--4--5-|
        [ window(close)   ]
        +-----+-----+-----+|
                    +4--5-|
              +2--3-|
        +----1|

    Examples:
        >>> res = window(lambda: reactivex.timer(0.5))

    Args:
        closing_mapper: A function invoked to define
            the closing of each produced window. It defines the
            boundaries of the produced windows (a window is started
            when the previous one is closed, resulting in
            non-overlapping windows).

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of windows.
    """
    from ._window import window_when_

    return window_when_(closing_mapper)


def window_toggle(
    openings: Observable[Any], closing_mapper: Callable[[Any], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    .. marble::
        :alt: window

        ---a-----------b------------|
           ---d--|
                       --------e-|
        ----1--2--3--4--5--6--7--8--|
        [ window(open, close)       ]
        ---+-----------+------------|
                       +5--6--7|
           +1-|

    >>> res = window(reactivex.interval(0.5), lambda i: reactivex.timer(i))

    Args:
        openings: Observable sequence whose elements denote the
            creation of windows.
        closing_mapper: A function invoked to define the closing of each
            produced window. Value from openings Observable that initiated
            the associated window is provided as argument to the function.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of windows.
    """
    from ._window import window_toggle_

    return window_toggle_(openings, closing_mapper)


def window_with_count(
    count: int, skip: Optional[int] = None
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on element count information.

    .. marble::
        :alt: window_with_count

        ---1-2-3---4-5-6--->
        [    window(3)     ]
        --+-------+-------->
                  +4-5-6-|
          +1-2-3-|

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
    from ._windowwithcount import window_with_count_

    return window_with_count_(count, skip)


def window_with_time(
    timespan: typing.RelativeTime,
    timeshift: Optional[typing.RelativeTime] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    from ._windowwithtime import window_with_time_

    return window_with_time_(timespan, timeshift, scheduler)


def window_with_time_or_count(
    timespan: typing.RelativeTime,
    count: int,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    from ._windowwithtimeorcount import window_with_time_or_count_

    return window_with_time_or_count_(timespan, count, scheduler)


def with_latest_from(
    *sources: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Any]]:
    """The `with_latest_from` operator.

    Merges the specified observable sequences into one observable
    sequence by creating a tuple only when the first
    observable sequence produces an element. The observables can be
    passed either as separate arguments or as a list.

    .. marble::
        :alt: with_latest_from

        ---1---2---3----4-|
        --a-----b----c-d----|
        [with_latest_from() ]
        ---1,a-2,a-3,b--4,d-|

    Examples:
        >>> op = with_latest_from(obs1)
        >>> op = with_latest_from([obs1, obs2, obs3])

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the result of
        combining elements of the sources into a tuple.
    """
    from ._withlatestfrom import with_latest_from_

    return with_latest_from_(*sources)


def zip(*args: Observable[Any]) -> Callable[[Observable[Any]], Observable[Any]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    .. marble::
        :alt: zip

        --1--2---3-----4---|
        -a----b----c-d------|
        [       zip()       ]
        --1,a-2,b--3,c-4,d-|


    Example:
        >>> res = zip(obs1, obs2)

    Args:
        args: Observable sources to zip.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence containing the result of
        combining elements of the sources as a tuple.
    """
    from ._zip import zip_

    return zip_(*args)


def zip_with_iterable(
    second: Iterable[_T2],
) -> Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]:
    """Merges the specified observable sequence and list into one
    observable sequence by creating a tuple whenever all of
    the observable sequences have produced an element at a
    corresponding index.

    .. marble::
        :alt: zip_with_iterable

        --1---2----3---4---|
        [   zip(a,b,c,b)   ]
        --1,a-2,b--3,c-4,d-|

    Example
        >>> res = zip([1,2,3])

    Args:
        second: Iterable to zip with the source observable..

    Returns:
        An operator function that takes and observable source and
        returns an observable sequence containing the result of
        combining elements of the sources as a tuple.
    """
    from ._zip import zip_with_iterable_

    return zip_with_iterable_(second)


zip_with_list = zip_with_iterable

__all__ = [
    "all",
    "amb",
    "as_observable",
    "average",
    "buffer",
    "buffer_when",
    "buffer_toggle",
    "buffer_with_count",
    "buffer_with_time",
    "buffer_with_time_or_count",
    "catch",
    "combine_latest",
    "concat",
    "contains",
    "count",
    "debounce",
    "throttle_with_timeout",
    "default_if_empty",
    "delay_subscription",
    "delay_with_mapper",
    "dematerialize",
    "delay",
    "distinct",
    "distinct_until_changed",
    "do",
    "do_action",
    "do_while",
    "element_at",
    "element_at_or_default",
    "exclusive",
    "expand",
    "filter",
    "filter_indexed",
    "finally_action",
    "find",
    "find_index",
    "first",
    "first_or_default",
    "flat_map",
    "flat_map_indexed",
    "flat_map_latest",
    "fork_join",
    "group_by",
    "group_by_until",
    "group_join",
    "ignore_elements",
    "is_empty",
    "join",
    "last",
    "last_or_default",
    "map",
    "map_indexed",
    "materialize",
    "max",
    "max_by",
    "merge",
    "merge_all",
    "min",
    "min_by",
    "multicast",
    "observe_on",
    "on_error_resume_next",
    "pairwise",
    "partition",
    "partition_indexed",
    "pluck",
    "pluck_attr",
    "publish",
    "publish_value",
    "reduce",
    "ref_count",
    "repeat",
    "replay",
    "retry",
    "sample",
    "scan",
    "sequence_equal",
    "share",
    "single",
    "single_or_default",
    "single_or_default_async",
    "skip",
    "skip_last",
    "skip_last_with_time",
    "skip_until",
    "skip_until_with_time",
    "skip_while",
    "skip_while_indexed",
    "skip_with_time",
    "slice",
    "some",
    "starmap",
    "starmap_indexed",
    "start_with",
    "subscribe_on",
    "sum",
    "switch_latest",
    "take",
    "take_last",
    "take_last_buffer",
    "take_last_with_time",
    "take_until",
    "take_until_with_time",
    "take_while",
    "take_while_indexed",
    "take_with_time",
    "throttle_first",
    "throttle_with_mapper",
    "timestamp",
    "timeout",
    "timeout_with_mapper",
    "time_interval",
    "to_dict",
    "to_future",
    "to_iterable",
    "to_list",
    "to_marbles",
    "to_set",
    "while_do",
    "window",
    "window_when",
    "window_toggle",
    "window_with_count",
    "window_with_time",
    "window_with_time_or_count",
    "with_latest_from",
    "zip",
    "zip_with_list",
    "zip_with_iterable",
    "zip_with_list",
]
