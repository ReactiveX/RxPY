# By design, pylint: disable=C0302
from datetime import datetime, timedelta
from typing import Callable, Any, Iterable, List, Union
from abc import abstractmethod

from rx import config
from .typing import Selector, Predicate
from .anonymousobserver import AnonymousObserver
from .blockingobservable import BlockingObservable
from . import typing as ty, bases


class ObservableBase(ty.Observable):
    """Observables base class.

    Represents a push-style collection and contains all operators as
    methods to allow classic Rx chaining of operators."""

    def __init__(self):
        self.lock = config["concurrency"].RLock()

    def __add__(self, other):
        """Pythonic version of concat

        Example:
        zs = xs + ys
        Returns self.concat(other)"""
        from ..operators.observable.concat import concat
        return concat(self, other)

    def __getitem__(self, key):
        """Slices the given observable using Python slice notation. The
        arguments to slice is start, stop and step given within brackets [] and
        separated with the ':' character. It is basically a wrapper around the
        operators skip(), skip_last(), take(), take_last() and filter().

        This marble diagram helps you remember how slices works with streams.
        Positive numbers is relative to the start of the events, while negative
        numbers are relative to the end (close) of the stream.

        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1   0

        Example:
        result = source[1:10]
        result = source[1:-2]
        result = source[1:-1:2]

        Keyword arguments:
        key -- Slice object

        Returns a sliced observable sequence.
        """

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
        elif isinstance(key, int):
            start, stop, step = key, key + 1, 1
        else:
            raise TypeError("Invalid argument type.")

        source = self
        from ..operators.observable.slice import slice as slice_
        return slice_(source, start, stop, step)

    def __iadd__(self, other):
        """Pythonic use of concat

        Example:
        xs += ys

        Returns self.concat(self, other)"""
        from ..operators.observable.concat import concat
        return concat(self, other)

    def __mul__(self, num: int):
        """Pythonic version of repeat.

        Example:
        yx = xs * 5

        Returns self.repeat(num)"""

        return self.repeat(num)

    def __or__(self, other):
        """Forward pipe operator."""
        return other(self)

    def subscribe(self, observer: ty.Observer = None,
                  scheduler: ty.Scheduler = None) -> ty.Disposable:
        """Subscribe an observer to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe(observer)

        Keyword arguments:
        observer -- [Optional] The object that is to receive
            notifications.

        Return disposable object representing an observer's subscription
        to the observable sequence.
        """
        from .subscribe import subscribe
        source = self
        return subscribe(source, observer, scheduler)

    def subscribe_callbacks(self, send: ty.Send = None, throw: ty.Throw = None,
                            close: ty.Close = None, scheduler: ty.Scheduler = None
                           ) -> ty.Disposable:
        """Subscribe callbacks to the observable sequence.

        Examples:
        1 - source.subscribe_callbacks(send)
        2 - source.subscribe_callbacks(send, throw)
        3 - source.subscribe_callbacks(send, throw, close)

        Keyword arguments:
        send -- [Optional] Action to invoke for each element in the
            observable sequence.
        throw -- [Optional] Action to invoke upon exceptional
            termination of the observable sequence.
        close -- [Optional] Action to invoke upon graceful
            termination of the observable sequence.

        Return disposable object representing an observer's subscription
        to the observable sequence.
        """
        observer = AnonymousObserver(send, throw, close)
        return self.subscribe(observer, scheduler)

    @abstractmethod
    def _subscribe_core(self, observer, scheduler=None):
        return NotImplemented

    def all(self, predicate):
        """Determines whether all elements of an observable sequence satisfy a
        condition.

        1 - res = source.all(lambda value: value.length > 3)

        Keyword arguments:
        predicate -- A function to test each element for a condition.

        Returns an observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
        """
        from ..operators.observable.all import all as all_
        source = self
        return all_(source, predicate)

    def amb(self, other):
        """Propagates the observable sequence that reacts first.

        other -- Other observable sequence.

        Returns an observable sequence that surfaces either of the given
        sequences, whichever reacted first.
        """
        from ..operators.observable.amb import _amb
        source = self
        return _amb(source, other)

    def and_(self, right):
        """Creates a pattern that matches when both observable sequences
        have an available value.

        Keyword arguments:
        right -- Observable sequence to match with the current sequence.

        Returns Pattern object that matches when both observable
        sequences have an available value.
        """
        from ..operators.observable.and_ import and_
        source = self
        return and_(source, right)

    def as_observable(self) -> 'ObservableBase':
        """Hides the identity of an observable sequence.

        Returns an observable sequence that hides the identity of the
        source sequence.
        """
        from ..operators.observable.asobservable import as_observable
        source = self
        return as_observable(source)

    def average(self, key_selector=None) -> 'ObservableBase':
        """Computes the average of an observable sequence of values that are in
        the sequence or obtained by invoking a transform function on each
        element of the input sequence if present.

        Example
        res = source.average();
        res = source.average(lambda x: x.value)

        Keyword arguments:
        key_selector -- A transform function to apply to each element.

        Returns an observable sequence containing a single element with
        the average of the sequence of values.
        """
        from ..operators.observable.average import average
        source = self
        return average(source, key_selector)

    def buffer(self, buffer_openings=None, buffer_closing_selector=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or more
        buffers.

        Keyword arguments:
        buffer_openings -- Observable sequence whose elements denote the
            creation of windows.
        buffer_closing_selector -- [optional] A function invoked to define
            the closing of each produced window. If a closing selector
            function is specified for the first parameter, this parameter is
            ignored.

        Returns an observable sequence of windows.
        """
        from ..operators.observable.buffer import buffer
        source = self
        return buffer(source, buffer_openings, buffer_closing_selector)

    def buffer_with_count(self, count: int, skip: int = None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or more
        buffers which are produced based on element count information.

        Example:
        res = xs.buffer_with_count(10)
        res = xs.buffer_with_count(10, 1)

        Keyword parameters:
        count -- {Number} Length of each buffer.
        skip -- {Number} [Optional] Number of elements to skip between
            creation of consecutive buffers. If not provided, defaults to
            the count.

        Returns an observable {Observable} sequence of buffers.
        """
        from ..operators.observable.buffer import buffer_with_count
        source = self
        return buffer_with_count(source, count, skip)

    def buffer_with_time(self, timespan, timeshift=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or more
        buffers which are produced based on timing information.

        # non-overlapping segments of 1 second
        1 - res = xs.buffer_with_time(1000)
        # segments of 1 second with time shift 0.5 seconds
        2 - res = xs.buffer_with_time(1000, 500)

        Keyword arguments:
        timespan -- Length of each buffer (specified as an integer denoting
            milliseconds).
        timeshift -- [Optional] Interval between creation of consecutive
            buffers (specified as an integer denoting milliseconds), or an
            optional scheduler parameter. If not specified, the time shift
            corresponds to the timespan parameter, resulting in non-overlapping
            adjacent buffers.

        Returns an observable sequence of buffers.
        """
        from ..operators.observable.bufferwithtime import buffer_with_time
        source = self
        return buffer_with_time(source, timespan, timeshift)

    def buffer_with_time_or_count(self, timespan, count) -> 'ObservableBase':
        """Projects each element of an observable sequence into a buffer that
        is completed when either it's full or a given amount of time has
        elapsed.

        # 5s or 50 items in an array
        1 - res = source.buffer_with_time_or_count(5000, 50)
        # 5s or 50 items in an array
        2 - res = source.buffer_with_time_or_count(5000, 50, Scheduler.timeout)

        Keyword arguments:
        timespan -- Maximum time length of a buffer.
        count -- Maximum element count of a buffer.
        scheduler -- [Optional] Scheduler to run bufferin timers on. If not
            specified, the timeout scheduler is used.

        Returns an observable sequence of buffers.
        """
        from ..operators.observable.bufferwithtimeorcount import buffer_with_time_or_count
        source = self
        return buffer_with_time_or_count(source, timespan, count)

    def combine_latest(self, observables: Union['ObservableBase', Iterable['ObservableBase']],
                       selector: Callable[[Any], Any]) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable
        sequence by using the selector function whenever any of the
        observable sequences produces an element. This can be in the form of
        an argument list of observables or an array.

        1 - obs = observable.combine_latest(obs1, obs2, obs3,
                                            lambda o1, o2, o3: o1 + o2 + o3)
        2 - obs = observable.combine_latest([obs1, obs2, obs3],
                                            lambda o1, o2, o3: o1 + o2 + o3)

        Returns an observable sequence containing the result of combining
        elements of the sources using the specified result selector
        function.
        """
        from ..operators.observable.combinelatest import combine_latest
        if isinstance(observables, ty.Observable):
            observables = [observables]

        args = [self] + list(observables)
        return combine_latest(args, selector)

    def catch_exception(self, second=None, handler=None):
        """Continues an observable sequence that is terminated by an exception
        with the next observable sequence.

        1 - xs.catch_exception(ys)
        2 - xs.catch_exception(lambda ex: ys(ex))

        Keyword arguments:
        handler -- Exception handler function that returns an observable
            sequence  given the error that occurred in the first sequence.
        second -- Second observable sequence used to produce results when an
            error occurred in the first sequence.

        Returns an observable sequence containing the first sequence's
        elements, followed by the elements of the handler sequence in case an
        exception occurred.
        """
        from ..operators.observable.catch import catch_exception
        source = self
        return catch_exception(source, second, handler)

    def concat(self, *args: 'ObservableBase') -> 'ObservableBase':
        """Concatenates all the observable sequences. This takes in either an
        array or variable arguments to concatenate.

        1 - concatenated = xs.concat(ys, zs)

        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        from ..operators.observable.concat import concat
        source = self
        return concat(source, *args)

    def concat_all(self) -> 'ObservableBase':
        """Concatenates an observable sequence of observable sequences.

        Returns an observable sequence that contains the elements of each
        observed inner sequence, in sequential order.
        """
        return self.merge(max_concurrent=1)

    def concat_map(self, mapper: Callable[[Any], Any]) -> 'ObservableBase':
        """Maps each emission to an Observable and fires its emissions.
        It will only fire each resulting Observable sequentially.
        The next derived Observable will not start its emissions until
        the current one calls close
        """
        return self.map(mapper).concat_all()

    def contains(self, value: Any, comparer=None) -> 'ObservableBase':
        """Determines whether an observable sequence contains a
        specified element with an optional equality comparer.

        Example
        1 - res = source.contains(42)
        2 - res = source.contains({ "value": 42 }, lambda x, y: x["value"] == y["value")

        Keyword parameters:
        value -- The value to locate in the source sequence.
        comparer -- [Optional] An equality comparer to compare elements.

        Returns an observable  sequence containing a single element
        determining whether the source sequence contains an element that
        has the specified value.
        """
        from ..operators.observable.contains import contains
        source = self
        return contains(source, value, comparer)

    def count(self, predicate=None) -> 'ObservableBase':
        """Returns an observable sequence containing a value that represents
        how many elements in the specified observable sequence satisfy a
        condition if provided, else the count of items.

        1 - res = source.count()
        2 - res = source.count(lambda x: x > 3)

        Keyword arguments:
        predicate -- A function to test each element for a condition.

        Returns an observable sequence containing a single element with a
        number that represents how many elements in the input sequence
        satisfy the condition in the predicate function if provided, else
        the count of items in the sequence.
        """
        from ..operators.observable.count import count
        source = self
        return count(source, predicate)

    def controlled(self, enable_queue: bool = True, scheduler=None):
        """Attach a controller to the observable sequence

        Attach a controller to the observable sequence with the ability to
        queue.

        Example:
        source = rx.Observable.interval(100).controlled()
        source.request(3) # Reads 3 values

        Keyword arguments:
        enable_queue -- truthy value to determine if values should
            be queued pending the next request
        scheduler -- determines how the requests will be scheduled

        Returns the observable sequence which only propagates values on request.
        """
        from ..backpressure.controlled import controlled
        source = self
        return controlled(source, enable_queue, scheduler)

    def default_if_empty(self, default_value=None) -> 'ObservableBase':
        """Returns the elements of the specified sequence or the
        specified value in a singleton sequence if the sequence is
        empty.

        obs = xs.default_if_empty()
        obs = xs.default_if_empty(False)

        Keyword arguments:
        default_value -- The value to return if the sequence is empty. If not
            provided, this defaults to None.

        Returns an observable sequence that contains the specified
        default value if the source is empty otherwise, the elements of
        the source itself.
        """
        from ..operators.observable.defaultifempty import default_if_empty
        source = self
        return default_if_empty(source, default_value)

    def delay(self, duetime):
        """Time shifts the observable sequence by duetime. The relative time
        intervals between the values are preserved.

        1 - res = rx.Observable.delay(datetime())
        2 - res = rx.Observable.delay(5000)

        Keyword arguments:
        duetime -- Absolute (specified as a datetime object) or relative
            time (specified as an integer denoting milliseconds) by which
            to shift the observable sequence.

        Returns time-shifted sequence.
        """
        from ..operators.observable.delay import delay
        source = self
        return delay(source, duetime)

    def delay_subscription(self, duetime: Union[datetime, int]) -> 'ObservableBase':
        """Time shifts the observable sequence by delaying the subscription.

        1 - res = source.delay_subscription(5000) # 5s

        duetime -- Absolute or relative time to perform the subscription at.

        Returns time-shifted sequence.
        """
        from ..operators.observable.delay_subscription import delay_subscription
        source = self
        return delay_subscription(source, duetime)

    def delay_with_selector(self, subscription_delay=None,
                            delay_duration_selector=None) -> 'ObservableBase':
        """Time shifts the observable sequence based on a subscription delay
        and a delay selector function for each element.

        # with selector only
        1 - res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
        # with delay and selector
        2 - res = source.delay_with_selector(Observable.timer(2000),
                                            lambda x: Observable.timer(x))

        subscription_delay -- [Optional] Sequence indicating the delay for the
            subscription to the source.
        delay_duration_selector [Optional] Selector function to retrieve a
            sequence indicating the delay for each given element.

        Returns time-shifted sequence.
        """
        from ..operators.observable.delaywithselector import delay_with_selector
        source = self
        return delay_with_selector(source, subscription_delay, delay_duration_selector)

    def dematerialize(self) -> 'ObservableBase':
        """Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Returns an observable sequence exhibiting the behavior
        corresponding to the source sequence's notification values.
        """
        from ..operators.observable.dematerialize import dematerialize
        source = self
        return dematerialize(source)

    def distinct(self, key_selector=None, comparer=None) -> 'ObservableBase':
        """Returns an observable sequence that contains only distinct
        elements according to the key_selector and the comparer. Usage
        of this operator should be considered carefully due to the
        maintenance of an internal lookup structure which can grow
        large.

        Example:
        res = obs = xs.distinct()
        obs = xs.distinct(lambda x: x.id)
        obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)

        Keyword arguments:
        key_selector -- [Optional]  A function to compute the comparison
            key for each element.
        comparer -- [Optional]  Used to compare items in the collection.

        Returns an observable sequence only containing the distinct
        elements, based on a computed key value, from the source
        sequence.
        """
        from ..operators.observable.distinct import distinct
        source = self
        return distinct(source, key_selector, comparer)

    def distinct_until_changed(self, key_selector=None, comparer=None) -> 'ObservableBase':
        """Returns an observable sequence that contains only distinct
        contiguous elements according to the key_selector and the
        comparer.

        1 - obs = observable.distinct_until_changed()
        2 - obs = observable.distinct_until_changed(lambda x: x.id)
        3 - obs = observable.distinct_until_changed(lambda x: x.id,
                                                    lambda x, y: x == y)

        key_selector -- [Optional] A function to compute the comparison
            key for each element. If not provided, it projects the
            value.
        comparer -- [Optional] Equality comparer for computed key
            values. If not provided, defaults to an equality comparer
            function.

        Return an observable sequence only containing the distinct
        contiguous elements, based on a computed key value, from the source
        sequence.
        """
        from ..operators.observable.distinctuntilchanged import distinct_until_changed
        source = self
        return distinct_until_changed(source, key_selector, comparer)

    def do(self, observer: ty.Observer) -> 'ObservableBase':
        """Invokes an action for each element in the observable sequence
        and invokes an action on graceful or exceptional termination of
        the observable sequence. This method can be used for debugging,
        logging, etc. of query behavior by intercepting the message
        stream to run arbitrary actions for messages on the pipeline.

        1 - observable.do(observer)

        observer -- Observer

        Returns the source sequence with the side-effecting behavior
        applied.
        """
        from ..operators.observable.do import do
        source = self
        return do(source, observer)

    def do_action(self, send=None, throw=None, close=None) -> 'ObservableBase':
        """Invokes an action for each element in the observable sequence
        and invokes an action on graceful or exceptional termination of
        the observable sequence. This method can be used for debugging,
        logging, etc. of query behavior by intercepting the message
        stream to run arbitrary actions for messages on the pipeline.

        1 - observable.do_action(send)
        2 - observable.do_action(send, throw)
        3 - observable.do_action(send, throw, close)

        send -- [Optional] Action to invoke for each element in the
            observable sequence.
        throw -- [Optional] Action to invoke on exceptional termination
            of the observable sequence.
        close -- [Optional] Action to invoke on graceful termination
            of the observable sequence.

        Returns the source sequence with the side-effecting behavior
        applied.
        """
        from ..operators.observable.do import do_action
        source = self
        return do_action(source, send, throw, close)

    def do_while(self, condition: Callable[[Any], bool]) -> 'ObservableBase':
        """Repeats source as long as condition holds emulating a do while loop.

        Keyword arguments:
        condition -- {Function} The condition which determines if the source
            will be repeated.

        Returns an observable {Observable} sequence which is repeated as long
        as the condition holds.
        """
        from ..operators.observable.dowhile import do_while
        source = self
        return do_while(condition, source)

    def element_at(self, index: int) -> 'ObservableBase':
        """Returns the element at a specified index in a sequence.

        Example:
        res = source.element_at(5)

        Keyword arguments:
        index -- The zero-based index of the element to retrieve.

        Returns an observable  sequence that produces the element at the
        specified position in the source sequence.
        """
        from ..operators.observable.elementat import element_at
        source = self
        return element_at(source, index)

    def element_at_or_default(self, index: int, default_value: Any = None) -> 'ObservableBase':
        """Returns the element at a specified index in a sequence or a
        default value if the index is out of range.

        Example:
        res = source.element_at_or_default(5)
        res = source.element_at_or_default(5, 0)

        Keyword arguments:
        index -- The zero-based index of the element to retrieve.
        default_value -- [Optional] The default value if the index is
            outside the bounds of the source sequence.

        Returns an observable sequence that produces the element at the
            specified position in the source sequence, or a default value if
            the index is outside the bounds of the source sequence.
        """
        from ..operators.observable.elementatordefault import element_at_or_default
        source = self
        return element_at_or_default(source, index, default_value)

    def exclusive(self) -> 'ObservableBase':
        """Performs a exclusive waiting for the first to finish before
        subscribing to another observable. Observables that come in between
        subscriptions will be dropped on the floor.

        Returns an exclusive observable with only the results that
        happen when subscribed.
        """
        from ..operators.observable.exclusive import exclusive
        source = self
        return exclusive(source)

    def filter(self, predicate: Callable[[Any], bool]) -> 'ObservableBase':
        """Filters the elements of an observable sequence based on a
        predicate.

        1 - source.filter(lambda value: value < 10)

        Keyword arguments:
        predicate -- A function to test each source element for a
            condition.

        Returns an observable sequence that contains elements from the
        input sequence that satisfy the condition.
        """
        from ..operators.observable.filter import filter as _filter
        source = self
        return _filter(predicate, source)

    def filter_indexed(self, predicate: Callable[[Any, int], bool]) -> 'ObservableBase':
        """Filters the elements of an observable sequence based on a
        predicate by incorporating the element's index.

        1 - source.filter(lambda value, index: value < 10 or index < 10)

        Keyword arguments:
        predicate - A function to test each source element for a
            condition; the second parameter of the function represents
            the index of the source element.

        Returns an observable sequence that contains elements from the
        input sequence that satisfy the condition.
        """

        from ..operators.observable.filter import filter_indexed
        source = self
        return filter_indexed(predicate, source)

    def finally_action(self, action) -> 'ObservableBase':
        """Invokes a specified action after the source observable sequence
        terminates gracefully or exceptionally.

        Example:
        res = observable.finally(lambda: print('sequence ended')

        Keyword arguments:
        action -- {Function} Action to invoke after the source observable
            sequence terminates.
        Returns {Observable} Source sequence with the action-invoking
        termination behavior applied.
        """
        from ..operators.observable.finallyaction import finally_action
        source = self
        return finally_action(source, action)

    def find(self, predicate: Predicate) -> 'ObservableBase':
        """Searches for an element that matches the conditions defined by the
        specified predicate, and returns the first occurrence within the entire
        Observable sequence.

        Keyword arguments:
        predicate -- {Function} The predicate that defines the conditions of the
            element to search for.

        Returns an Observable {Observable} sequence with the first element that
        matches the conditions defined by the specified predicate, if found
        otherwise, None.
        """
        from ..operators.observable.find import find
        source = self
        return find(source, predicate)

    def first(self, predicate=None) -> 'ObservableBase':
        """Returns the first element of an observable sequence that
        satisfies the condition in the predicate if present else the
        first item in the sequence.

        Example:
        res = res = source.first()
        res = res = source.first(lambda x: x > 3)

        Keyword arguments:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

        Returns Observable sequence containing the first element in the
        observable sequence that satisfies the condition in the
        predicate if provided, else the first item in the sequence.
        """
        from ..operators.observable.first import first
        source = self
        return first(source, predicate)

    def first_or_default(self, predicate=None, default_value=None) -> 'ObservableBase':
        """Returns the first element of an observable sequence that
        satisfies the condition in the predicate, or a default value if
        no such element exists.

        Example:
        res = source.first_or_default()
        res = source.first_or_default(lambda x: x > 3)
        res = source.first_or_default(lambda x: x > 3, 0)
        res = source.first_or_default(null, 0)

        Keyword arguments:
        predicate -- [optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- [Optional] The default value if no such element
            exists.  If not specified, defaults to None.

        Returns {Observable} Sequence containing the first element in
        the observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
        """
        from ..operators.observable.firstordefault import first_or_default
        source = self
        return first_or_default(source, predicate, default_value)

    def flat_map(self, selector: Callable[[Any], Any],
                 result_selector: Callable=None) -> 'ObservableBase':
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
        from ..operators.observable.flatmap import flat_map
        source = self
        return flat_map(source, selector, result_selector)

    def flat_map_indexed(self, selector: Callable[[Any, int], Any],
                         result_selector: Callable=None) -> 'ObservableBase':
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
        from ..operators.observable.flatmap import flat_map_indexed
        source = self
        return flat_map_indexed(source, selector, result_selector)

    def is_empty(self) -> 'ObservableBase':
        """Determines whether an observable sequence is empty.

        Returns an observable sequence containing a single element
        determining whether the source sequence is empty.
        """

        return self.some().map(lambda b: not b)

    def last(self, predicate=None) -> 'ObservableBase':
        """Returns the last element of an observable sequence that satisfies the
        condition in the predicate if specified, else the last element.

        Example:
        res = source.last()
        res = source.last(lambda x: x > 3)

        Keyword arguments:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

        Returns sequence containing the last element in the observable
        sequence that satisfies the condition in the predicate.
        """
        from ..operators.observable.last import last
        source = self
        return last(source, predicate)

    def last_or_default(self, predicate=None, default_value=None) -> 'ObservableBase':
        """Return last or default element.

        Returns the last element of an observable sequence that satisfies
        the condition in the predicate, or a default value if no such
        element exists.

        Examples:
        res = source.last_or_default()
        res = source.last_or_default(lambda x: x > 3)
        res = source.last_or_default(lambda x: x > 3, 0)
        res = source.last_or_default(None, 0)

        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- [Optional] The default value if no such element
            exists. If not specified, defaults to None.

        Returns Observable sequence containing the last element in the
        observable sequence that satisfies the condition in the predicate,
        or a default value if no such element exists.
        """
        from ..operators.observable.lastordefault import last_or_default
        source = self
        return last_or_default(source, predicate, default_value)

    def map(self, mapper: Callable[[Any], Any]) -> 'ObservableBase':
        """Project each element of an observable sequence into a new
        form.

        1 - source.map(lambda value: value * value)

        Keyword arguments:
        mapper -- A transform function to apply to each source element.

        Returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source.
        """

        from ..operators.observable.map import map as _map
        source = self
        return _map(mapper, source)

    def map_indexed(self, mapper: Callable[[Any, int], Any]) -> 'ObservableBase':
        from ..operators.observable.map import map_indexed
        source = self
        return map_indexed(mapper, source)

    def materialize(self) -> 'ObservableBase':
        """Materializes the implicit notifications of an observable sequence as
        explicit notification values.

        Returns an observable sequence containing the materialized notification
        values from the source sequence.
        """
        from ..operators.observable.materialize import materialize
        source = self
        return materialize(source)

    def merge(self, *args, max_concurrent=None):
        """Merges an observable sequence of observable sequences into an
        observable sequence, limiting the number of concurrent subscriptions
        to inner sequences. Or merges two observable sequences into a single
        observable sequence.

        1 - merged = sources.merge(max_concurrent=1)
        2 - merged = source.merge(other_source)

        Keyword arguments:
        max_concurrent -- [Optional] Maximum number of inner observable
            sequences being subscribed to concurrently or the second
            observable sequence.

        Returns the observable sequence that merges the elements of the
        inner sequences.
        """
        from ..operators.observable.merge import merge
        source = self
        return merge(source, *args, max_concurrent=max_concurrent)

    def merge_all(self) -> 'ObservableBase':
        """Merges an observable sequence of observable sequences into an
        observable sequence.

        Returns the observable sequence that merges the elements of the inner
        sequences.
        """
        from ..operators.observable.merge import merge_all
        source = self
        return merge_all(source)

    def max(self, comparer=None):
        """Returns the maximum value in an observable sequence according to the
        specified comparer.

        Example
        res = source.max()
        res = source.max(lambda x, y:  x.value - y.value)

        Keyword arguments:
        comparer -- {Function} [Optional] Comparer used to compare elements.

        Returns {Observable} An observable sequence containing a single element
        with the maximum element in the source sequence.
        """
        from ..operators.observable.max import max as max_
        source = self
        return max_(source, comparer)

    def max_by(self, key_selector, comparer=None) -> 'ObservableBase':
        """Returns the elements in an observable sequence with the maximum
        key value according to the specified comparer.

        Example
        res = source.max_by(lambda x: x.value)
        res = source.max_by(lambda x: x.value, lambda x, y: x - y)

        Keyword arguments:
        key_selector -- {Function} Key selector function.
        comparer -- {Function} [Optional] Comparer used to compare key values.

        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a maximum key value.
        """
        from ..operators.observable.maxby import max_by
        source = self
        return max_by(source, key_selector, comparer)

    def min(self, comparer=None) -> 'ObservableBase':
        """Returns the minimum element in an observable sequence according to
        the optional comparer else a default greater than less than check.

        Example
        res = source.min()
        res = source.min(lambda x, y: x.value - y.value)

        comparer -- {Function} [Optional] Comparer used to compare elements.

        Returns an observable sequence {Observable} containing a single element
        with the minimum element in the source sequence.
        """
        from ..operators.observable.min import min as min_
        source = self
        return min_(source, comparer)

    def min_by(self, key_selector: Selector, comparer=None) -> 'ObservableBase':
        """Returns the elements in an observable sequence with the minimum key
        value according to the specified comparer.

        Example
        res = source.min_by(lambda x: x.value)
        res = source.min_by(lambda x: x.value, lambda x, y: x - y)

        Keyword arguments:
        key_selector -- {Function} Key selector function.
        comparer -- {Function} [Optional] Comparer used to compare key values.

        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a minimum key value.
        """
        from ..operators.observable.minby import min_by
        source = self
        return min_by(source, key_selector, comparer)

    def multicast(self, subject=None, subject_selector=None, selector=None) -> 'ObservableBase':
        """Multicasts the source sequence notifications through an instantiated
        subject into all uses of the sequence within a selector function. Each
        subscription to the resulting sequence causes a separate multicast
        invocation, exposing the sequence resulting from the selector function's
        invocation. For specializations with fixed subject types, see Publish,
        PublishLast, and Replay.

        Example:
        1 - res = source.multicast(observable)
        2 - res = source.multicast(subject_selector=lambda scheduler: Subject(),
                                selector=lambda x: x)

        Keyword arguments:
        subject_selector -- {Function} Factory function to create an
            intermediate subject through which the source sequence's elements
            will be multicast to the selector function.
        subject -- Subject {Subject} to push source elements into.
        selector -- {Function} [Optional] Optional selector function which can
            use the multicasted source sequence subject to the policies enforced
            by the created subject. Specified only if subject_selector" is a
            factory function.

        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        from ..operators.observable.multicast import multicast
        source = self
        return multicast(source, subject, subject_selector, selector)

    def observe_on(self, scheduler: bases.Scheduler) -> 'ObservableBase':
        """Wraps the source sequence in order to run its observer callbacks on
        the specified scheduler.

        Keyword arguments:
        scheduler -- Scheduler to notify observers on.

        Returns the source sequence whose observations happen on the specified
        scheduler.

        This only invokes observer callbacks on a scheduler. In case the
        subscription and/or unsubscription actions have side-effects
        that require to be run on a scheduler, use subscribe_on.
        """
        from ..operators.observable.observeon import observe_on
        source = self
        return observe_on(source, scheduler)

    def partition(self, predicate: Callable[[Any], Any]) -> List['ObservableBase']:
        """Returns two observables which partition the observations of the
        source by the given function. The first will trigger observations for
        those values for which the predicate returns true. The second will
        trigger observations for those values where the predicate returns false.
        The predicate is executed once for each subscribed observer. Both also
        propagate all error observations arising from the source and each
        completes when the source completes.

        Keyword arguments:
        predicate -- The function to determine which output Observable will
            trigger a particular observation.

        Returns a list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate returns False.
        """
        from ..operators.observable.partition import partition
        source = self
        return partition(source, predicate)

    def partition_indexed(self, predicate: Callable[[Any, int], Any]) -> List['ObservableBase']:
        """Returns two observables which partition the observations of the
        source by the given function. The first will trigger observations for
        those values for which the predicate returns true. The second will
        trigger observations for those values where the predicate returns false.
        The predicate is executed once for each subscribed observer. Both also
        propagate all error observations arising from the source and each
        completes when the source completes.

        Keyword arguments:
        predicate -- The function to determine which output Observable will
            trigger a particular observation.

        Returns a list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate returns False.
        """
        from ..operators.observable.partition import partition_indexed
        source = self
        return partition_indexed(source, predicate)

    def publish(self, selector=None) -> 'ObservableBase':
        """Returns an observable sequence that is the result of invoking the
        selector on a connectable observable sequence that shares a single
        subscription to the underlying sequence. This operator is a
        specialization of Multicast using a regular Subject.

        Example:
        res = source.publish()
        res = source.publish(lambda x: x)

        selector -- [Optional] Selector function which can use the
            multicasted source sequence as many times as needed, without
            causing multiple subscriptions to the source sequence.
            Subscribers to the given source will receive all
            notifications of the source from the time of the
            subscription on.

        Returns an observable sequence that contains the elements of
        a sequence produced by multicasting the source sequence
        within a selector function."""

        from ..operators.observable.publish import publish
        source = self
        return publish(source, selector)

    def reduce(self, accumulator: Callable[[Any, Any], Any], seed: Any=None) -> 'ObservableBase':
        """Applies an accumulator function over an observable sequence,
        returning the result of the aggregation as a single element in the
        result sequence. The specified seed value is used as the initial
        accumulator value.

        For aggregation behavior with incremental intermediate results, see
        Observable.scan.

        Example:
        1 - res = source.reduce(lambda acc, x: acc + x)
        2 - res = source.reduce(lambda acc, x: acc + x, 0)

        Keyword arguments:
        :param types.FunctionType accumulator: An accumulator function to be
            invoked on each element.
        :param T seed: Optional initial accumulator value.

        :returns: An observable sequence containing a single element with the
            final accumulator value.
        :rtype: Observable
        """
        from ..operators.observable.reduce import reduce
        source = self
        return reduce(source, accumulator, seed)

    aggregate = reduce

    def repeat(self, repeat_count=None) -> 'ObservableBase':
        """Repeats the observable sequence a specified number of times. If the
        repeat count is not specified, the sequence repeats indefinitely.

        1 - repeated = source.repeat()
        2 - repeated = source.repeat(42)

        Keyword arguments:
        repeat_count -- Number of times to repeat the sequence. If not
            provided, repeats the sequence indefinitely.

        Returns the observable sequence producing the elements of the given
        sequence repeatedly."""

        from rx.internal.iterable import Iterable as CoreIterable
        from ..operators.observable.concat import concat
        from .observable import Observable
        return Observable.defer(lambda _: concat(CoreIterable.repeat(self, repeat_count)))

    def scan(self, accumulator: Callable[[Any, Any], Any], seed: Any=None) -> 'ObservableBase':
        """Applies an accumulator function over an observable sequence and
        returns each intermediate result. The optional seed value is used as
        the initial accumulator value. For aggregation behavior with no
        intermediate results, see Observable.aggregate.

        1 - scanned = source.scan(lambda acc, x: acc + x)
        2 - scanned = source.scan(lambda acc, x: acc + x, 0)

        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each
            element.
        seed -- [Optional] The initial accumulator value.

        Returns an observable sequence containing the accumulated
        values.
        """
        from ..operators.observable.scan import scan
        source = self
        return scan(source, accumulator, seed)

    def select_switch(self, selector: Callable) -> 'ObservableBase':
        """Projects each element of an observable sequence into a new sequence
        of observable sequences by incorporating the element's index and then
        transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.

        Keyword arguments:
        selector -- {Function} A transform function to apply to each source
            element; the second parameter of the function represents the index
            of the source element.

        Returns an observable {Observable} sequence whose elements are the
        result of invoking the transform function on each element of source
        producing an Observable of Observable sequences and that at any point in
        time produces the elements of the most recent inner observable sequence
        that has been received.
        """
        return self.map(selector).switch_latest()

    flat_map_latest = select_switch
    switch_map = select_switch

    def sequence_equal(self, second: 'ObservableBase',
                   comparer: Callable[[Any, Any], bool] = None) -> 'ObservableBase':
        """Determines whether two sequences are equal by comparing the
        elements pairwise using a specified equality comparer.

        1 - res = source.sequence_equal([1,2,3])
        2 - res = source.sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
        3 - res = source.sequence_equal(Observable.return_value(42))
        4 - res = source.sequence_equal(Observable.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

        second -- Second observable sequence or array to compare.
        comparer -- [Optional] Comparer used to compare elements of both
            sequences. No guarantees on order of comparer arguments.

        Returns an observable sequence that contains a single element which
        indicates whether both sequences are of equal length and their
        corresponding elements are equal according to the specified equality
        comparer.
        """
        from ..operators.observable.sequenceequal import sequence_equal
        source = self
        return sequence_equal(source, second, comparer)

    def share(self):
        """Share a single subscription among multple observers.

        Returns a new Observable that multicasts (shares) the original
        Observable. As long as there is at least one Subscriber this
        Observable will be subscribed and emitting data. When all
        subscribers have unsubscribed it will unsubscribe from the source
        Observable.

        This is an alias for Observable.publish().ref_count().
        """
        return self.publish().ref_count()

    def skip(self, count: int) -> 'ObservableBase':
        """Bypasses a specified number of elements in an observable
        sequence and then returns the remaining elements.

        Keyword arguments:
        count -- The number of elements to skip before returning the
            remaining elements.

        Returns an observable sequence that contains the elements that
        occur after the specified index in the input sequence.
        """
        from ..operators.observable.skip import skip
        source = self
        return skip(count, source)

    def skip_last(self, count: int) -> 'ObservableBase':
        """Bypasses a specified number of elements in an observable
        sequence and then returns the remaining elements.

        Keyword arguments:
        count -- The number of elements to skip before returning the
            remaining elements.

        Returns an observable sequence that contains the elements that
        occur after the specified index in the input sequence.
        """
        from ..operators.observable.skiplast import skip_last
        source = self
        return skip_last(count, source)

    def skip_while(self, predicate: Callable[[Any], Any]) -> 'ObservableBase':
        """Bypasses elements in an observable sequence as long as a specified
        condition is true and then returns the remaining elements. The
        element's index is used in the logic of the predicate function.

        1 - source.skip_while(lambda value: value < 10)
        2 - source.skip_while(lambda value, index: value < 10 or index < 10)

        predicate -- A function to test each element for a condition; the
            second parameter of the function represents the index of the
            source element.

        Returns an observable sequence that contains the elements from the
        input sequence starting at the first element in the linear series that
        does not pass the test specified by predicate.
        """
        from ..operators.observable.skipwhile import skip_while
        source = self
        return skip_while(source, predicate)

    def skip_while_indexed(self, predicate: Callable[[Any, int], Any]) -> 'ObservableBase':
        """Bypasses elements in an observable sequence as long as a specified
        condition is true and then returns the remaining elements. The
        element's index is used in the logic of the predicate function.

        1 - source.skip_while(lambda value, index: value < 10 or index < 10)

        predicate -- A function to test each element for a condition; the
            second parameter of the function represents the index of the
            source element.

        Returns an observable sequence that contains the elements from the
        input sequence starting at the first element in the linear series that
        does not pass the test specified by predicate.
        """
        from ..operators.observable.skipwhile import skip_while_indexed
        source = self
        return skip_while_indexed(source, predicate)

    def some(self, predicate=None) -> 'ObservableBase':
        """Determines whether some element of an observable sequence satisfies a
        condition if present, else if some items are in the sequence.

        Example:
        result = source.some()
        result = source.some(lambda x: x > 3)

        Keyword arguments:
        predicate -- A function to test each element for a condition.

        Returns an observable sequence containing a single element
        determining whether some elements in the source sequence pass the test
        in the specified predicate if given, else if some items are in the
        sequence.
        """
        from ..operators.observable.some import some
        source = self
        return some(source, predicate)

    def start_with(self, *args: Any) -> 'ObservableBase':
        """Prepends a sequence of values to an observable.

        1 - source.start_with(1, 2, 3)

        Returns the source sequence prepended with the specified values.
        """
        from ..operators.observable.startswith import start_with
        source = self
        return start_with(source, *args)

    def switch_latest(self) -> 'ObservableBase':
        """Transforms an observable sequence of observable sequences
        into an observable sequence producing values only from the most
        recent observable sequence.

        Returns the observable sequence that at any point in time
        produces the elements of the most recent inner observable
        sequence that has been received.
        """
        from ..operators.observable.switchlatest import switch_latest
        sources = self
        return switch_latest(sources)

    def take(self, count: int) -> 'ObservableBase':
        """Returns a specified number of contiguous elements from the
        start of an observable sequence.

        1 - source.take(5)

        Keyword arguments:
        count -- The number of elements to return.

        Returns an observable sequence that contains the specified
        number of elements from the start of the input sequence.
        """
        from ..operators.observable.take import take
        source = self
        return take(count, source)

    def take_last(self, count: int) -> 'ObservableBase':
        """Returns a specified number of contiguous elements from the
        end of an observable sequence.

        Example:
        res = source.take_last(5)

        Description:
        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence,
        this buffer is drained on the result sequence. This causes the
        elements to be delayed.

        Keyword arguments:
        count - Number of elements to take from the end of the source
            sequence.

        Returns an observable sequence containing the specified number
            of elements from the end of the source sequence.
        """
        from ..operators.observable.takelast import take_last
        source = self
        return take_last(count, source)

    def take_last_buffer(self, count) -> 'ObservableBase':
        """Returns an array with the specified number of contiguous elements
        from the end of an observable sequence.

        Example:
        res = source.take_last(5)

        Description:
        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence, this
        buffer is drained on the result sequence. This causes the elements to be
        delayed.

        Keyword arguments:
        count -- Number of elements to take from the end of the source
            sequence.

        Returns: An observable sequence containing a single list with the specified
        number of elements from the end of the source sequence.
        """
        from ..operators.observable.takelastbuffer import take_last_buffer
        source = self
        return take_last_buffer(source, count)

    def take_last_with_time(self, duration) -> 'ObservableBase':
        """Returns elements within the specified duration from the end of the
        observable source sequence.

        Example:
        res = source.take_last_with_time(5000)

        Description:
        This operator accumulates a queue with a length enough to store elements
        received during the initial duration window. As more elements are
        received, elements older than the specified duration are taken from the
        queue and produced on the result sequence. This causes elements to be
        delayed with duration.

        Keyword arguments:
        duration -- {Number} Duration for taking elements from the end of the
            sequence.

        Returns an observable sequence with the elements taken
        during the specified duration from the end of the source sequence.
        """
        from ..operators.observable.takelastwithtime import take_last_with_time
        source = self
        return take_last_with_time(source, duration)

    def take_while(self, predicate: Callable[[Any], Any]) -> 'ObservableBase':
        """Returns elements from an observable sequence as long as a
        specified condition is true. The element's index is used in the
        logic of the predicate function.

        1 - source.take_while(lambda value: value < 10)

        Keyword arguments:
        predicate -- A function to test each element for a condition;
            the second parameter of the function represents the index of
            the source element.

        Returns an observable sequence that contains the elements from
        the input sequence that occur before the element at which the
        test no longer passes.
        """
        from ..operators.observable.takewhile import take_while
        source = self
        return take_while(source, predicate)

    def take_while_indexed(self, predicate: Callable[[Any, int], Any]) -> 'ObservableBase':
        """Returns elements from an observable sequence as long as a specified
        condition is true. The element's index is used in the logic of the
        predicate function.

        1 - source.take_while(lambda value, index: value < 10 or index < 10)

        Keyword arguments:
        predicate -- A function to test each element for a condition; the
            second parameter of the function represents the index of the source
            element.

        Returns an observable sequence that contains the elements from the
        input sequence that occur before the element at which the test no
        longer passes.
        """
        from ..operators.observable.takewhile import take_while_indexed
        source = self
        return take_while_indexed(source, predicate)

    def then_do(self, selector: Selector) -> 'ObservableBase':
        """Matches when the observable sequence has an available value and
        projects the value.

        selector -- Selector that will be invoked for values in the source
            sequence.

        Returns Plan that produces the projected values, to be fed (with
        other plans) to the when operator.
        """
        from ..operators.observable.thendo import then_do
        source = self
        return then_do(source, selector)

    then = then_do

    def throttle_first(self, window_duration: Union[timedelta, int]) -> 'ObservableBase':
        """Returns an Observable that emits only the first item emitted
        by the source Observable during sequential time windows of a
        specified duration.

        Keyword arguments:
        window_duration -- time to wait before emitting another item
            after emitting the last item.
        Returns an Observable that performs the throttle operation.
        """

        from ..operators.observable.throttlefirst import throttle_first
        source = self
        return throttle_first(source, window_duration)

    def throttle_with_timeout(self, duetime) -> 'ObservableBase':
        """Ignores values from an observable sequence which are followed
        by another value before duetime.

        Example:
        1 - res = source.throttle_with_timeout(5000) # 5 seconds

        Keyword arguments:
        duetime -- {Number} Duration of the throttle period for each
            value (specified as an integer denoting milliseconds).

        Returns the throttled sequence.
        """
        from ..operators.observable.debounce import throttle_with_timeout
        source = self
        return throttle_with_timeout(source, duetime)

    debounce = throttle_with_timeout

    def throttle_with_selector(self, throttle_duration_selector) -> 'ObservableBase':
        """Ignores values from an observable sequence which are followed
        by another value within a computed throttle duration.

        1 - res = source.throttle_with_selector(lambda x: rx.Scheduler.timer(x+x))

        Keyword arguments:
        throttle_duration_selector -- Selector function to retrieve a
            sequence indicating the throttle duration for each given
            element.

        Returns the throttled sequence.
        """
        from ..operators.observable.debounce import throttle_with_selector
        source = self
        return throttle_with_selector(source, throttle_duration_selector)

    def throw_resume_next(self, second) -> 'ObservableBase':
        """Continues an observable sequence that is terminated normally
        or by an exception with the next observable sequence.

        Keyword arguments:
        second -- Second observable sequence used to produce results
            after the first sequence terminates.

        Returns an observable sequence that concatenates the first and
        second sequence, even if the first sequence terminates
        exceptionally.
        """

        if not second:
            raise Exception('Second observable is required')

        from ..operators.observable.onerrorresumenext import throw_resume_next
        return throw_resume_next([self, second])

    def time_interval(self) -> 'ObservableBase':
        """Records the time interval between consecutive values in an
        observable sequence.

        1 - res = source.time_interval()

        Return An observable sequence with time interval information on
        values.
        """
        from ..operators.observable.timeinterval import time_interval
        source = self
        return time_interval(source)

    def timeout(self, duetime: Union[int, datetime], other: 'ObservableBase' = None) -> 'ObservableBase':
        """Returns the source observable sequence or the other
        observable sequence if duetime elapses.

        1 - res = source.timeout(5000); # 5 seconds
        # As a date and timeout observable
        2 - res = source.timeout(datetime(), Observable.return_value(42))
        # 5 seconds and timeout observable
        3 - res = source.timeout(5000, Observable.return_value(42))
        # As a date and timeout observable

        Keyword arguments:
        duetime -- Absolute (specified as a datetime object) or relative
            time (specified as an integer denoting milliseconds) when a
            timeout occurs.
        other -- Sequence to return in case of a timeout. If not
            specified, a timeout error throwing sequence will be used.

        Returns the source sequence switching to the other sequence in
        case of a timeout.
        """
        from ..operators.observable.timeout import timeout
        source = self
        return timeout(source, duetime, other)

    def timeout_with_selector(self, first_timeout=None,
                            timeout_duration_selector=None, other=None) -> 'ObservableBase':
        """Returns the source observable sequence, switching to the
        other observable sequence if a timeout is signaled.

        1 - res = source.timeout_with_selector(rx.Observable.timer(500))
        2 - res = source.timeout_with_selector(rx.Observable.timer(500),
                    lambda x: rx.Observable.timer(200))
        3 - res = source.timeout_with_selector(rx.Observable.timer(500),
                    lambda x: rx.Observable.timer(200)),
                    rx.Observable.return_value(42))

        Keyword arguments:
        first_timeout -- [Optional] Observable sequence that represents
            the timeout for the first element. If not provided, this
            defaults to Observable.never().
        timeout_Duration_selector -- [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the
            current element and the next element.
        other -- [Optional] Sequence to return in case of a timeout. If
            not provided, this is set to Observable.throw().

        Returns the source sequence switching to the other sequence in
        case of a timeout.
        """
        from ..operators.observable.timeoutwithselector import timeout_with_selector
        source = self
        return timeout_with_selector(source, first_timeout, timeout_duration_selector, other)

    def timestamp(self) -> 'ObservableBase':
        """Records the timestamp for each value in an observable
        sequence.

        1 - res = source.timestamp() # produces objects with attributes
            "value" and "timestamp", where value is the original value.

        Returns an observable sequence with timestamp information on
        values.
        """
        from ..operators.observable.timestamp import timestamp
        source = self
        return timestamp(source)

    def to_blocking(self) -> BlockingObservable:
        from ..operators.observable.toblocking import to_blocking
        source = self
        return to_blocking(source)

    def to_iterable(self) -> 'ObservableBase':
        """Creates an iterable from an observable sequence.

        Returns an observable sequence containing a single element with
        a list containing all the elements of the source sequence.
        """
        from ..operators.observable.toiterable import to_iterable
        source = self
        return to_iterable(source)

    def window(self, window_openings=None, window_closing_selector=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or
        more windows.

        Keyword arguments:
        window_openings -- Observable sequence whose elements denote the
            creation of windows.
        window_closing_selector -- [Optional] A function invoked to
            define the closing of each produced window. It defines the
            boundaries of the produced windows (a window is started when
            the previous one is closed, resulting in non-overlapping
            windows).

        Returns an observable sequence of windows.
        """
        from ..operators.observable.window import window
        source = self
        return window(source, window_openings, window_closing_selector)

    def window_with_count(self, count, skip=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or more
        windows which are produced based on element count information.

        1 - xs.window_with_count(10)
        2 - xs.window_with_count(10, 1)

        count -- Length of each window.
        skip -- [Optional] Number of elements to skip between creation of
            consecutive windows. If not specified, defaults to the count.

        Returns an observable sequence of windows.
        """
        from ..operators.observable.windowwithcount import window_with_count
        source = self
        return window_with_count(source, count, skip)

    def window_with_time(self, timespan, timeshift=None) -> 'ObservableBase':
        from ..operators.observable.windowwithtime import window_with_time
        source = self
        return window_with_time(source, timespan, timeshift)

    def window_with_time_or_count(self, timespan, count) -> 'ObservableBase':
        from ..operators.observable.windowwithtimeorcount import window_with_time_or_count
        source = self
        return window_with_time_or_count(source, timespan, count)

    def with_latest_from(self, observables: Union['ObservableBase', Iterable['ObservableBase']],
                         selector: Callable[[Any], Any]) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable sequence
        by using the selector function only when the source observable sequence
        (the instance) produces an element. The other observables can be passed
        either as seperate arguments or as a list.

        1 - obs = observable.with_latest_from(obs, lambda o1, o2: o1 + o2)

        2 - obs = observable.with_latest_from([obs1, obs2],
                                            lambda o1, o2, o3: o1 + o2 + o3)

        Returns an observable sequence containing the result of combining
        elements of the sources using the specified result selector function.
        """
        from ..operators.observable.withlatestfrom import with_latest_from
        if isinstance(observables, ty.Observable):
            observables = [observables]

        sources = [self] + list(observables)
        return with_latest_from(sources, selector)

    def zip(self, *args: 'Union[Iterable[Any], ObservableBase]',
            result_selector: Selector = None) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable
        sequence by using the selector function whenever all of the
        observable sequences or an array have produced an element at a
        corresponding index.

        The last element in the arguments must be a function to invoke for
        each series of elements at corresponding indexes in the sources.

        1 - res = obs1.zip(obs2, result_selector=fn)
        2 - res = x1.zip([1,2,3], result_selector=fn)

        Keyword arguments:
        args -- Observable sources to zip together with self.
        result_selector -- Selector function that produces an element
            whenever all of the observable sequences have produced an
            element at a corresponding index

        Returns an observable sequence containing the result of combining
        elements of the sources using the specified result selector
        function.
        """
        from ..operators.observable.zip import zip as _zip
        source = self

        return _zip(source, *args, result_selector=result_selector)
