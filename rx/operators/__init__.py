# pylint: disable=too-many-lines,redefined-outer-name,redefined-builtin

from asyncio import Future
from typing import Callable, Union, Any, Iterable, List, Optional, cast, overload
from datetime import timedelta, datetime

from rx.internal.utils import NotSet
from rx.core import Observable, ConnectableObservable, GroupedObservable, typing, pipe
from rx.core.typing import Mapper, MapperIndexed, Predicate, PredicateIndexed, Comparer, Accumulator
from rx.subject import Subject


def all(predicate: Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.all import _all
    return _all(predicate)


def amb(right_source: Observable) -> Callable[[Observable], Observable]:
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


def average(key_mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.average import _average
    return _average(key_mapper)


def buffer(boundaries: Observable) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more buffers.

    .. marble::
        :alt: buffer

        ---a-----b-----c--------|
        --1--2--3--4--5--6--7---|
        [       buffer()        ]
        ---1-----2,3---4,5------|

    Examples:
        >>> res = buffer(rx.interval(1.0))

    Args:
        boundaries: Observable sequence whose elements denote the
            creation and completion of buffers.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """
    from rx.core.operators.buffer import _buffer
    return _buffer(boundaries)


def buffer_when(closing_mapper: Callable[[], Observable]) -> Callable[[Observable], Observable]:
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
        >>> res = buffer_when(lambda: rx.timer(0.5))

    Args:
        closing_mapper: A function invoked to define the closing of each
            produced buffer. A buffer is started when the previous one is
            closed, resulting in non-overlapping buffers. The buffer is closed
            when one item is emitted or when the observable completes.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of windows.
    """
    from rx.core.operators.buffer import _buffer_when
    return _buffer_when(closing_mapper)


def buffer_toggle(openings: Observable,
                  closing_mapper: Callable[[Any], Observable]
                  ) -> Callable[[Observable], Observable]:
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

    >>> res = buffer_toggle(rx.interval(0.5), lambda i: rx.timer(i))

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
    from rx.core.operators.buffer import _buffer_toggle
    return _buffer_toggle(openings, closing_mapper)


def buffer_with_count(count: int, skip: Optional[int] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.buffer import _buffer_with_count
    return _buffer_with_count(count, skip)


def buffer_with_time(timespan: typing.RelativeTime,
                     timeshift: Optional[typing.RelativeTime] = None,
                     scheduler: Optional[typing.Scheduler] = None
                     ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.bufferwithtime import _buffer_with_time
    return _buffer_with_time(timespan, timeshift, scheduler)


def buffer_with_time_or_count(timespan, count, scheduler=None) -> Callable[[Observable], Observable]:
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
        >>> res = source.buffer_with_time_or_count(5.0, 50)
        >>> # 5s or 50 items in an array
        >>> res = source.buffer_with_time_or_count(5.0, 50, Scheduler.timeout)

    Args:
        timespan: Maximum time length of a buffer.
        count: Maximum element count of a buffer.
        scheduler: [Optional] Scheduler to run buffering timers on. If
            not specified, the timeout scheduler is used.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of buffers.
    """
    from rx.core.operators.bufferwithtimeorcount import _buffer_with_time_or_count
    return _buffer_with_time_or_count(timespan, count, scheduler)


def catch(handler: Union[Observable, Callable[[Exception, Observable], Observable]]
          ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.catch import _catch
    return _catch(handler)


def combine_latest(*others: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.combinelatest import _combine_latest
    return _combine_latest(*others)


def concat(*sources: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.concat import _concat
    return _concat(*sources)


def contains(value: Any,
             comparer: Optional[typing.Comparer] = None
             ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.contains import _contains
    return _contains(value, comparer)


def count(predicate: Optional[typing.Predicate] = None) -> Callable[[Observable], Observable]:
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

    from rx.core.operators.count import _count
    return _count(predicate)


def debounce(duetime: typing.RelativeTime,
             scheduler: Optional[typing.Scheduler] = None
             ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.debounce import _debounce
    return _debounce(duetime, scheduler)


throttle_with_timeout = debounce


def default_if_empty(default_value: Any = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.defaultifempty import _default_if_empty
    return _default_if_empty(default_value)


def delay_subscription(duetime: typing.AbsoluteOrRelativeTime,
                       scheduler: Optional[typing.Scheduler] = None
                      ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.delaysubscription import _delay_subscription
    return _delay_subscription(duetime, scheduler=scheduler)


def delay_with_mapper(subscription_delay=None,
                      delay_duration_mapper=None
                      ) -> Callable[[Observable], Observable]:
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
        >>> res = source.delay_with_mapper(rx.timer(2.0), lambda x: rx.timer(x))

    Args:
        subscription_delay: [Optional] Sequence indicating the delay
            for the subscription to the source.
        delay_duration_mapper: [Optional] Selector function to retrieve
            a sequence indicating the delay for each given element.

    Returns:
        A function that takes an observable source and returns a
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


def delay(duetime: typing.RelativeTime,
          scheduler: Optional[typing.Scheduler] = None
          ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.delay import _delay
    return _delay(duetime, scheduler)


def distinct(key_mapper: Optional[Mapper] = None,
             comparer: Optional[Comparer] = None
             ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.distinct import _distinct
    return _distinct(key_mapper, comparer)


def distinct_until_changed(key_mapper: Optional[Mapper] = None,
                           comparer: Optional[Comparer] = None
                           ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.distinctuntilchanged import _distinct_until_changed
    return _distinct_until_changed(key_mapper, comparer)


def do(observer: typing.Observer) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.do import do as do_
    return do_(observer)


def do_action(on_next: Optional[typing.OnNext] = None,
              on_error: Optional[typing.OnError] = None,
              on_completed: Optional[typing.OnCompleted] = None
              ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.do import _do_action
    return _do_action(on_next, on_error, on_completed)


def do_while(condition: Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.dowhile import _do_while
    return _do_while(condition)


def element_at(index: int) -> Callable[[Observable], Observable]:
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
        returns an observable  sequence that produces the element at
        the specified position in the source sequence.
    """
    from rx.core.operators.elementatordefault import _element_at_or_default
    return _element_at_or_default(index, False)


def element_at_or_default(index: int, default_value: Any = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.elementatordefault import _element_at_or_default
    return _element_at_or_default(index, True, default_value)


def exclusive() -> Callable[[Observable], Observable]:
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
    from rx.core.operators.exclusive import _exclusive
    return _exclusive()


def expand(mapper: Mapper) -> Callable[[Observable], Observable]:
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


def filter(predicate: Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.filter import _filter
    return _filter(predicate)


def filter_indexed(predicate_indexed: Optional[PredicateIndexed] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.filter import _filter_indexed
    return _filter_indexed(predicate_indexed)


def finally_action(action: Callable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.finallyaction import _finally_action
    return _finally_action(action)


def find(predicate: Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.find import _find_value
    return _find_value(predicate, False)


def find_index(predicate: Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.find import _find_value
    return _find_value(predicate, True)


def first(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.first import _first
    return _first(predicate)


def first_or_default(predicate: Optional[Predicate] = None,
                     default_value: Any = None
                     ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.firstordefault import _first_or_default
    return _first_or_default(predicate, default_value)


def flat_map(mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.flatmap import _flat_map
    return _flat_map(mapper)


def flat_map_indexed(mapper_indexed: Optional[MapperIndexed] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.flatmap import _flat_map_indexed
    return _flat_map_indexed(mapper_indexed)


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


def group_by(key_mapper: Mapper,
             element_mapper: Optional[Mapper] = None,
             subject_mapper: Optional[Callable[[], Subject]] = None,
             ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.groupby import _group_by
    return _group_by(key_mapper, element_mapper, subject_mapper)


def group_by_until(key_mapper: Mapper,
                   element_mapper: Optional[Mapper],
                   duration_mapper: Callable[[GroupedObservable], Observable],
                   subject_mapper: Optional[Callable[[], Subject]] = None,
                   ) -> Callable[[Observable], Observable]:
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
        >>> group_by_until(lambda x: x.id, None, lambda : rx.never())
        >>> group_by_until(lambda x: x.id, lambda x: x.name, lambda grp: rx.never())
        >>> group_by_until(lambda x: x.id, lambda x: x.name, lambda grp: rx.never(), lambda: ReplaySubject())

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
    from rx.core.operators.groupbyuntil import _group_by_until
    return _group_by_until(key_mapper, element_mapper, duration_mapper, subject_mapper)


def group_join(right: Observable,
               left_duration_mapper: Callable[[Any], Observable],
               right_duration_mapper: Callable[[Any], Observable]
               ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.groupjoin import _group_join
    return _group_join(right, left_duration_mapper, right_duration_mapper)


def ignore_elements() -> Callable[[Observable], Observable]:
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
    from rx.core.operators.ignoreelements import _ignore_elements
    return _ignore_elements()


def is_empty() -> Callable[[Observable], Observable]:
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
    from rx.core.operators.isempty import _is_empty
    return _is_empty()


def join(right: Observable,
         left_duration_mapper: Callable[[Any], Observable],
         right_duration_mapper: Callable[[Any], Observable]
         ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.join import _join
    return _join(right, left_duration_mapper, right_duration_mapper)


def last(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.last import _last
    return _last(predicate)


def last_or_default(predicate: Optional[Predicate] = None,
                    default_value: Any = None
                    ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.lastordefault import _last_or_default
    return  _last_or_default(predicate, default_value)


def map(mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.map import _map
    return _map(mapper)


def map_indexed(mapper_indexed: Optional[MapperIndexed] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.map import _map_indexed
    return _map_indexed(mapper_indexed)


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


def max(comparer: Optional[Comparer] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.max import _max
    return _max(comparer)


def max_by(key_mapper: Mapper,
           comparer: Optional[Comparer] = None
           ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.maxby import _max_by
    return _max_by(key_mapper, comparer)


def merge(*sources: Observable,
          max_concurrent: Optional[int] = None
          ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.merge import _merge
    return _merge(*sources, max_concurrent=max_concurrent)


def merge_all() -> Callable[[Observable], Observable]:
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
    from rx.core.operators.merge import _merge_all
    return _merge_all()


def min(comparer: Optional[Comparer] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.min import _min
    return _min(comparer)


def min_by(key_mapper: Mapper,
           comparer: Optional[Comparer] = None
           ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.minby import _min_by
    return _min_by(key_mapper, comparer)


def multicast(subject: Optional[typing.Subject] = None,
              subject_factory: Optional[Callable[[Optional[typing.Scheduler]], typing.Subject]] = None,
              mapper: Optional[Callable[[ConnectableObservable], Observable]]  = None
              ) -> Callable[[Observable], Union[Observable, ConnectableObservable]]:
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


def observe_on(scheduler: typing.Scheduler) -> Callable[[Observable], Observable]:
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


def on_error_resume_next(second: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.partition import _partition
    return _partition(predicate)


def partition_indexed(predicate_indexed: PredicateIndexed) -> Callable[[Observable], List[Observable]]:
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
    from rx.core.operators.partition import _partition_indexed
    return _partition_indexed(predicate_indexed)


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


def publish(mapper: Optional[Mapper] = None) -> Callable[[Observable], ConnectableObservable]:
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


def publish_value(initial_value: Any, mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.publishvalue import _publish_value
    return _publish_value(initial_value, mapper)


def reduce(accumulator: Accumulator, seed: Any = NotSet) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.reduce import _reduce
    return _reduce(accumulator, seed)


def ref_count() -> Callable[[ConnectableObservable], Observable]:
    """Returns an observable sequence that stays connected to the
    source as long as there is at least one subscription to the
    observable sequence.
    """
    from rx.core.operators.connectable.refcount import _ref_count
    return _ref_count()


def repeat(repeat_count: Optional[int] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.repeat import _repeat
    return _repeat(repeat_count)


def replay(mapper: Optional[Mapper] = None,
           buffer_size: Optional[int] = None,
           window: Optional[typing.RelativeTime] = None,
           scheduler: Optional[typing.Scheduler] = None
           ) -> Callable[[Observable], Union[Observable, ConnectableObservable]]:
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
    from rx.core.operators.replay import _replay
    return _replay(mapper, buffer_size, window, scheduler=scheduler)


def retry(retry_count: Optional[int] = None) -> Callable[[Observable], Observable]:
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


def sample(sampler: Union[typing.RelativeTime, Observable],
           scheduler: Optional[typing.Scheduler] = None
           ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.sample import _sample
    return _sample(sampler, scheduler)


def scan(accumulator: Accumulator, seed: Any = NotSet) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.scan import _scan
    return _scan(accumulator, seed)


def sequence_equal(second: Observable, comparer: Optional[Comparer] = None
                   ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.publish import _share
    return _share()


def single(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.single import _single
    return _single(predicate)


def single_or_default(predicate: Optional[Predicate] = None,
                      default_value: Any = None
                      ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.singleordefault import _single_or_default
    return _single_or_default(predicate, default_value)


def single_or_default_async(has_default: bool = False,
                            default_value: Any = None
                            ) -> Callable[[Observable], Observable]:
    from rx.core.operators.singleordefault import _single_or_default_async
    return _single_or_default_async(has_default, default_value)


def skip(count: int) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skip import _skip
    return _skip(count)


def skip_last(count: int) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skiplast import _skip_last
    return _skip_last(count)


def skip_last_with_time(duration: typing.RelativeTime, scheduler: typing.Scheduler = None
                        ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skiplastwithtime import _skip_last_with_time
    return _skip_last_with_time(duration, scheduler=scheduler)


def skip_until(other: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skipuntil import _skip_until
    return _skip_until(other)


def skip_until_with_time(start_time: typing.AbsoluteOrRelativeTime,
                         scheduler: Optional[typing.Scheduler] = None
                        ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skipuntilwithtime import _skip_until_with_time
    return _skip_until_with_time(start_time, scheduler=scheduler)


def skip_while(predicate: typing.Predicate) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skipwhile import _skip_while
    return _skip_while(predicate)


def skip_while_indexed(predicate: typing.PredicateIndexed) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skipwhile import _skip_while_indexed
    return _skip_while_indexed(predicate)


def skip_with_time(duration: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None
                  ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.skipwithtime import _skip_with_time
    return _skip_with_time(duration, scheduler=scheduler)


def slice(start: Optional[int] = None,
          stop: Optional[int] = None,
          step: Optional[int] = None
          ) -> Callable[[Observable], Observable]:
    """The slice operator.

    Slices the given observable. It is basically a wrapper around the operators
    :func:`skip <rx.operators.skip>`,
    :func:`skip_last <rx.operators.skip_last>`,
    :func:`take <rx.operators.take>`,
    :func:`take_last <rx.operators.take_last>` and
    :func:`filter <rx.operators.filter>`.

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
    from rx.core.operators.slice import _slice
    return _slice(start, stop, step)


def some(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.some import _some
    return _some(predicate)


def starmap(mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
        return pipe()

    return pipe(map(lambda values: cast(Mapper, mapper)(*values)))


def starmap_indexed(mapper: Optional[MapperIndexed] = None
                    ) -> Callable[[Observable], Observable]:
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

    if mapper is None:
        return pipe()

    return pipe(map(lambda values: cast(MapperIndexed, mapper)(*values)))


def start_with(*args: Any) -> Callable[[Observable], Observable]:
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


def sum(key_mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.sum import _sum
    return _sum(key_mapper)


def switch_latest() -> Callable[[Observable], Observable]:
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
    from rx.core.operators.switchlatest import _switch_latest
    return _switch_latest()


def take(count: int) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.take import _take
    return _take(count)


def take_last(count: int) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takelast import _take_last
    return _take_last(count)


def take_last_buffer(count: int) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takelastbuffer import _take_last_buffer
    return _take_last_buffer(count)


def take_last_with_time(duration: typing.RelativeTime,
                        scheduler: Optional[typing.Scheduler] = None
                        ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takelastwithtime import _take_last_with_time
    return _take_last_with_time(duration, scheduler=scheduler)


def take_until(other: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takeuntil import _take_until
    return _take_until(other)


def take_until_with_time(end_time: typing.AbsoluteOrRelativeTime,
                         scheduler: Optional[typing.Scheduler] = None
                         ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takeuntilwithtime import _take_until_with_time
    return _take_until_with_time(end_time, scheduler=scheduler)


def take_while(predicate: Predicate, inclusive: bool = False) -> Callable[[Observable], Observable]:
    """Returns elements from an observable sequence as long as a
    specified condition is true. The element's index is used in the
    logic of the predicate function.

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
    from rx.core.operators.takewhile import _take_while
    return _take_while(predicate, inclusive)


def take_while_indexed(predicate: PredicateIndexed, inclusive: bool = False) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takewhile import _take_while_indexed
    return _take_while_indexed(predicate, inclusive)


def take_with_time(duration: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None
                  ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.takewithtime import _take_with_time
    return _take_with_time(duration, scheduler=scheduler)


def throttle_first(window_duration: typing.RelativeTime,
                   scheduler: Optional[typing.Scheduler] = None
                  ) -> Callable[[Observable], Observable]:
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
    return _throttle_first(window_duration, scheduler)


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


def timestamp(scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Observable]:
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
    return _timestamp(scheduler=scheduler)


def timeout(duetime: typing.AbsoluteTime,
            other: Optional[Observable] = None,
            scheduler: Optional[typing.Scheduler] = None
            ) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.timeout import _timeout
    return _timeout(duetime, other, scheduler)


def timeout_with_mapper(first_timeout: Optional[Observable] = None,
                        timeout_duration_mapper: Optional[Callable[[Any], Observable]] = None,
                        other: Optional[Observable] = None
                        ) -> Callable[[Observable], Observable]:
    """Returns the source observable sequence, switching to the other
    observable sequence if a timeout is signaled.

    Examples:
        >>> res = timeout_with_mapper(rx.timer(0.5))
        >>> res = timeout_with_mapper(rx.timer(0.5), lambda x: rx.timer(0.2))
        >>> res = timeout_with_mapper(rx.timer(0.5), lambda x: rx.timer(0.2)), rx.return_value(42))

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


def time_interval(scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.timeinterval import _time_interval
    return _time_interval(scheduler=scheduler)


def to_dict(key_mapper: Mapper, element_mapper: Optional[Mapper] = None
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


def to_future(future_ctor: Optional[Callable[[], Future]] = None) -> Callable[[Observable], Future]:
    """Converts an existing observable sequence to a Future.

    Example:
        op = to_future(asyncio.Future);

    Args:
        future_ctor: [Optional] The constructor of the future.

    Returns:
        An operator function that takes an observable source and returns
        a future with the last value from the observable sequence.
    """
    from rx.core.operators.tofuture import _to_future
    return _to_future(future_ctor)


def to_iterable() -> Callable[[Observable], Observable]:
    """Creates an iterable from an observable sequence.

    There is also an alias called ``to_list``.

    Returns:
        An operator function that takes an obserable source and
        returns an observable sequence containing a single element with
        an iterable containing all the elements of the source sequence.
    """
    from rx.core.operators.toiterable import _to_iterable
    return _to_iterable()


to_list = to_iterable


def to_marbles(timespan: typing.RelativeTime = 0.1,
               scheduler: Optional[typing.Scheduler] = None
               ) -> Callable[[Observable], Observable]:
    """Convert an observable sequence into a marble diagram string.

    Args:
        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Observable stream.
    """
    from rx.core.operators.tomarbles import _to_marbles
    return _to_marbles(scheduler=scheduler, timespan=timespan)


def to_set() -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a set.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence with a single value of a set
        containing the values from the observable sequence.
    """
    from rx.core.operators.toset import _to_set
    return _to_set()


def while_do(condition: Predicate) -> Callable[[Observable], Observable]:
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


def window(boundaries: Observable) -> Callable[[Observable], Observable]:
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
        >>> res = window(rx.interval(1.0))

    Args:
        boundaries: Observable sequence whose elements denote the
            creation and completion of non-overlapping windows.

    Returns:
        An operator function that takes an observable source and
        returns an observable sequence of windows.

    """
    from rx.core.operators.window import _window
    return _window(boundaries)


def window_when(closing_mapper: Callable[[], Observable]) -> Callable[[Observable], Observable]:
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
        >>> res = window(lambda: rx.timer(0.5))

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
    from rx.core.operators.window import _window_when
    return _window_when(closing_mapper)


def window_toggle(openings: Observable,
                  closing_mapper: Callable[[Any], Observable]
                  ) -> Callable[[Observable], Observable]:
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

    >>> res = window(rx.interval(0.5), lambda i: rx.timer(i))

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
    from rx.core.operators.window import _window_toggle
    return _window_toggle(openings, closing_mapper)


def window_with_count(count: int, skip: Optional[int] = None) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.windowwithcount import _window_with_count
    return _window_with_count(count, skip)


def window_with_time(timespan: typing.RelativeTime,
                     timeshift: Optional[typing.RelativeTime] = None,
                     scheduler: Optional[typing.Scheduler] = None
                     ) -> Callable[[Observable], Observable]:
    from rx.core.operators.windowwithtime import _window_with_time
    return _window_with_time(timespan, timeshift, scheduler)


def window_with_time_or_count(timespan: typing.RelativeTime, count: int,
                              scheduler: Optional[typing.Scheduler] = None
                              ) -> Callable[[Observable], Observable]:
    from rx.core.operators.windowwithtimeorcount import _window_with_time_or_count
    return _window_with_time_or_count(timespan, count, scheduler)


def with_latest_from(*sources: Observable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.withlatestfrom import _with_latest_from
    return _with_latest_from(*sources)


def zip(*args: Observable) -> Callable[[Observable], Observable]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    .. marble::
        :alt: zip

        --1--2---3-----4---|
        -a----b----c-d-----|
        [       zip()      ]
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
    from rx.core.operators.zip import _zip
    return _zip(*args)


def zip_with_iterable(second: Iterable) -> Callable[[Observable], Observable]:
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
    from rx.core.operators.zip import _zip_with_iterable
    return _zip_with_iterable(second)


zip_with_list = zip_with_iterable
