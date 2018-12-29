# By design, pylint: disable=C0302
import threading
from datetime import datetime, timedelta
from typing import Callable, Any, Iterable, List, Union, cast, overload
from asyncio import Future

from .typing import Mapper, MapperIndexed, Predicate, PredicateIndexed, Accumulator, Scheduler
from .disposable import Disposable
from .anonymousobserver import AnonymousObserver
from .blockingobservable import BlockingObservable
from . import typing, abc


class ObservableBase(typing.Observable):
    """Observables base class.

    Represents a push-style collection and contains all operators as
    methods to allow classic Rx chaining of operators."""

    def __init__(self, source: typing.Observable = None) -> None:
        self.lock = threading.RLock()
        self.source = source

    def __add__(self, other):
        """Pythonic version of concat.

        Example:
            >>> zs = xs + ys

        Returns:
            self.concat(other)"""
        from ..operators.observable.concat import concat
        return concat(self, other)

    def __await__(self) -> Any:
        """Awaits the given observable.

        Returns:
            The last item of the observable sequence.

        Raises:
            TypeError: If key is not of type int or slice
        """
        return iter(self.to_future())

    def __getitem__(self, key):
        """Slices the given observable using Python slice notation. The
        arguments to slice is start, stop and step given within brackets
        [] and separated with the ':' character. It is basically a
        wrapper around the operators skip(), skip_last(), take(),
        take_last() and filter().

        This marble diagram helps you remember how slices works with
        streams. Positive numbers is relative to the start of the
        events, while negative numbers are relative to the end (close)
        of the stream.

        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1   0

        Examples:
            >>> result = source[1:10]
            >>> result = source[1:-2]
            >>> result = source[1:-1:2]

        Args:
            key: Slice object

        Returns:
            A sliced observable sequence.
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
        """Pythonic use of concat.

        Example:
            xs += ys

        Returns:
            self.concat(self, other)
        """
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

    @overload
    def subscribe(self, observer: typing.Observer = None,
                  scheduler: typing.Scheduler = None
                  ) -> Disposable:
        raise NotImplementedError

    @overload
    def subscribe(self,  # pylint: disable=E0102,W0221
                  on_next: typing.OnNext = None,
                  on_error: typing.OnError = None,
                  on_completed: typing.OnCompleted = None,
                  scheduler: typing.Scheduler = None
                  ) -> Disposable:
        raise NotImplementedError

    def subscribe(self, *args, **kw) -> Disposable:  # pylint: disable=E0102,W0221
        """Subscribes an observer to the observable sequence.

        The observer may be specified as an observer or as individual
        callbacks for on_next, on_error and on_completed as specified
        in the examples below.

        Examples:
            >>> source.subscribe()
            >>> source.subscribe(observer)
            >>> source.subscribe(observer, scheduler)
            >>> source.subscribe(on_next)
            >>> source.subscribe(on_next, on_error)
            >>> source.subscribe(on_next, on_error, on_completed)
            >>> source.subscribe(on_next, on_error, on_completed, scheduler)

        Args:
            observer -- The object that is to receive notifications. You
                may subscribe using an observer or callbacks, not both.
            on_next -- Action to invoke for each element in the
                observable sequence.
            on_error -- Action to invoke upon exceptional termination of
                the observable sequence.
            on_completed -- Action to invoke upon graceful termination
                of the observable sequence.
            scheduler: The scheduler to use for this subscription.

        Returns:
            Disposable object representing an observer's subscription
            to the observable sequence.
        """

        observer = on_next = on_error = on_completed = scheduler = None

        if args:
            arg0 = args[0]
            if isinstance(arg0, abc.Observer) or (
                    not callable(arg0) and not isinstance(arg0, Scheduler)):
                observer = arg0
            else:
                on_next = arg0
                if len(args) > 1:
                    on_error = args[1]
                if len(args) > 2:
                    on_completed = args[2]

            if isinstance(args[-1], Scheduler):
                scheduler = args[-1]

        scheduler = cast(Scheduler, kw.get('scheduler')) or scheduler
        observer = kw.get('observer') or observer

        if not observer:
            on_next = kw.get('on_next') or on_next
            on_error = kw.get('on_error') or on_error
            on_completed = kw.get('on_completed') or on_completed
            observer = AnonymousObserver(on_next, on_error, on_completed)

        from .subscribe import subscribe
        return subscribe(self, observer, scheduler)

    def subscribe_(self,
                   on_next: typing.OnNext = None,
                   on_error: typing.OnError = None,
                   on_completed: typing.OnCompleted = None,
                   scheduler: typing.Scheduler = None
                   ) -> Disposable:
        """Subscribe callbacks to the observable sequence.

        Examples:
            >>> source.subscribe_(on_next)
            >>> source.subscribe_(on_next, on_error)
            >>> source.subscribe_(on_next, on_error, on_completed)

        Args:
            on_next: Action to invoke for each element in the observable
                sequence.
            on_error: Action to invoke upon exceptional termination of
                the observable sequence.
            on_completed: Action to invoke upon graceful termination of
                the observable sequence.
            scheduler: The scheduler to use for this subscription.

        Returns:
            Disposable object representing an observer's subscription
            to the observable sequence.
        """
        observer = AnonymousObserver(on_next, on_error, on_completed)

        from .subscribe import subscribe
        return subscribe(self, observer, scheduler)

    def _subscribe_core(self, observer, scheduler=None):
        return self.source.subscribe(observer, scheduler)

    def pipe(self, *operators: 'Callable[[ObservableBase], ObservableBase]') -> 'ObservableBase':
        """Compose multiple operators left to right.

        Composes zero or more operators into a functional composition.
        The operators are composed to right. A composition of zero
        operators gives back the original source.

        source.pipe() == source
        source.pipe(f) == f(source)
        source.pipe(g, f) == f(g(source))
        source.pipe(h, g, f) == f(g(h(source)))
        ...

        Returns the composed observable.
        """
        from .pipe import pipe
        return pipe(*operators)(self)

    def all(self, predicate):
        """Determines whether all elements of an observable sequence
        satisfy a condition.

        Examples:
            >>> res = source.all(lambda value: value.length > 3)

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            An observable sequence containing a single element
            determining whether all elements in the source sequence pass
            the test in the specified predicate.
        """
        from ..operators.observable.all import all as all_
        return all_(predicate)(self)

    def amb(self, other: abc.Observable) -> "ObservableBase":
        """Propagates the observable sequence that reacts first.

        Args:
            other: Other observable sequence.

        Returns:
            An observable sequence that surfaces either of the given
            sequences, whichever reacted first.
        """
        from ..operators.observable.amb import amb
        return amb(self, other)

    def and_(self, right):
        """Creates a pattern that matches when both observable sequences
        have an available value.

        Args:
            right: Observable sequence to match with the current
                sequence.

        Returns:
            Pattern object that matches when both observable sequences
            have an available value.
        """
        from ..operators.observable.and_ import and_
        return and_(self, right)

    def as_observable(self) -> 'ObservableBase':
        """Hides the identity of an observable sequence.

        Returns:
            An observable sequence that hides the identity of the
            source sequence.
        """
        from ..operators.observable.asobservable import as_observable
        source = self
        return as_observable(source)

    def average(self, key_mapper=None) -> 'ObservableBase':
        """Computes the average of an observable sequence of values that
        are in the sequence or obtained by invoking a transform function
        on each element of the input sequence if present.

        Examples:
            >>> res = source.average()
            >>> res = source.average(lambda x: x.value)

        Args:
            key_mapper: A transform function to apply to each element.

        Returns:
            An observable sequence containing a single element with
            the average of the sequence of values.
        """
        from ..operators.observable.average import average
        return average(key_mapper)(self)

    def buffer(self, buffer_openings=None, buffer_closing_mapper=None) -> 'ObservableBase':
        """
        Projects each element of an observable sequence into zero or
        more buffers.

        Args:
            buffer_openings: Observable sequence whose elements denote
                the creation of windows.
            buffer_closing_mapper: A function invoked to define the
                closing of each produced window. If a closing mapper
                function is specified for the first parameter, this
                parameter is ignored.

        Returns:
            An observable sequence of windows.
        """
        from ..operators.observable.buffer import buffer
        return buffer(buffer_openings, buffer_closing_mapper)(self)

    def buffer_with_count(self, count: int, skip: int = None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or
        more buffers which are produced based on element count
        information.

        Examples:
            >>> res = xs.buffer_with_count(10)
            >>> res = xs.buffer_with_count(10, 1)

        Args:
            count: Length of each buffer.
            skip: Number of elements to skip between creation of
                consecutive buffers. If not provided, defaults to the
                count.

        Returns:
            An observable sequence of buffers.
        """
        from ..operators.observable.buffer import buffer_with_count
        return buffer_with_count(count, skip)(self)

    def buffer_with_time(self, timespan, timeshift=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or
        more buffers which are produced based on timing information.

        Examples:
            # non-overlapping segments of 1 second
            >>> res = xs.buffer_with_time(1000)
            # segments of 1 second with time shift 0.5 seconds
            >>> res = xs.buffer_with_time(1000, 500)

        Args:
            timespan: Length of each buffer (specified as an integer
                denoting milliseconds).
            timeshift: Interval between creation of consecutive buffers
                (specified as an integer denoting milliseconds), or an
                optional scheduler parameter. If not specified, the time
                shift corresponds to the timespan parameter, resulting
                in non-overlapping adjacent buffers.

        Returns:
            An observable sequence of buffers.
        """
        from ..operators.observable.bufferwithtime import buffer_with_time
        return buffer_with_time(self, timespan, timeshift)

    def buffer_with_time_or_count(self, timespan, count) -> 'ObservableBase':
        """Projects each element of an observable sequence into a buffer that
        is completed when either it's full or a given amount of time has
        elapsed.

        >>> # 5s or 50 items in an array
        >>> res = source.buffer_with_time_or_count(5000, 50)
        >>> # 5s or 50 items in an array
        >>> res = source.buffer_with_time_or_count(5000, 50, Scheduler.timeout)

        Args:
            timespan -- Maximum time length of a buffer.
            count -- Maximum element count of a buffer.
            scheduler -- [Optional] Scheduler to run bufferin timers on.
                If not specified, the timeout scheduler is used.

        Returns:
            An observable sequence of buffers.
        """
        from ..operators.observable.bufferwithtimeorcount import buffer_with_time_or_count
        return buffer_with_time_or_count(self, timespan, count)

    def catch_exception(self, second=None, handler=None):
        """Continues an observable sequence that is terminated by an
        exception with the next observable sequence.

        Examples:
            >>> xs.catch_exception(ys)
            >>> xs.catch_exception(lambda ex: ys(ex))

        Args:
            handler -- Exception handler function that returns an
                observable sequence  given the error that occurred in
                the first sequence.
            second -- Second observable sequence used to produce results
                when an error occurred in the first sequence.

        Returns:
            An observable sequence containing the first sequence's
            elements, followed by the elements of the handler sequence
            in case an exception occurred.
        """
        from ..operators.observable.catch import catch_exception
        return catch_exception(second, handler)(self)

    def combine_latest(self, observables: Union['ObservableBase', Iterable['ObservableBase']],
                       mapper: Callable[[Any], Any]) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable
        sequence by using the mapper function whenever any of the
        observable sequences produces an element. This can be in the
        form of an argument list of observables or an array.

        Examples:
            >>> obs = observable.combine_latest(obs1, obs2, obs3, lambda o1, o2, o3: o1 + o2 + o3)
            >>> obs = observable.combine_latest([obs1, obs2, obs3], lambda o1, o2, o3: o1 + o2 + o3)

        Returns:
            An observable sequence containing the result of combining
            elements of the sources using the specified result mapper
            function.
        """
        from ..operators.observable.combinelatest import combine_latest
        if isinstance(observables, typing.Observable):
            observables = [observables]

        args = [self] + list(observables)
        return combine_latest(args, mapper)

    def concat(self, *args: 'ObservableBase') -> 'ObservableBase':
        """Concatenates all the observable sequences. This takes in
        either an array or variable arguments to concatenate.

        Example:
            >>> concatenated = xs.concat(ys, zs)

        Returns:
            An observable sequence that contains the elements of each
            given sequence, in sequential order.
        """
        from ..operators.observable.concat import concat
        source = self
        return concat(source, *args)

    def concat_all(self) -> 'ObservableBase':
        """Concatenates an observable sequence of observable sequences.

        Returns:
            An observable sequence that contains the elements of each
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

        Examples:
            >>> res = source.contains(42)
            >>> res = source.contains({ "value": 42 }, lambda x, y: x["value"] == y["value")

        Args:
            value: The value to locate in the source sequence.
            comparer: An equality comparer to compare elements.

        Returns:
            An observable  sequence containing a single element
            determining whether the source sequence contains an element
            that has the specified value.
        """
        from ..operators.observable.contains import contains
        return contains(value, comparer)(self)

    def count(self, predicate=None) -> 'ObservableBase':
        """Returns an observable sequence containing a value that
        represents how many elements in the specified observable
        sequence satisfy a condition if provided, else the count of
        items.

        Examples:
            >>> res = source.count()
            >>> res = source.count(lambda x: x > 3)

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            An observable sequence containing a single element with a
            number that represents how many elements in the input
            sequence satisfy the condition in the predicate function if
            provided, else the count of items in the sequence.
        """
        from ..operators.observable.count import count
        return count(predicate)(self)

    def controlled(self, enable_queue: bool = True, scheduler=None):
        """Attach a controller to the observable sequence.

        Attach a controller to the observable sequence with the ability
        to queue.

        Example:
            >>> source = rx.Observable.interval(100).controlled()
            >>> source.request(3) # Reads 3 values

        Args:
            enable_queue: truthy value to determine if values should
                be queued pending the next request
            scheduler: determines how the requests will be scheduled

        Returns:
            The observable sequence which only propagates values on
            request.
        """

        from ..backpressure.observableextensions import controlled
        return controlled(self, enable_queue, scheduler)

    def default_if_empty(self, default_value=None) -> 'ObservableBase':
        """Returns the elements of the specified sequence or the
        specified value in a singleton sequence if the sequence is
        empty.

        Examples:
            >>> obs = xs.default_if_empty()
            >>> obs = xs.default_if_empty(False)

        Args:
            default_value: The value to return if the sequence is empty.
                If not provided, this defaults to None.

        Returns:
            An observable sequence that contains the specified default
            value if the source is empty otherwise, the elements of the
            source itself.
        """
        from ..operators.observable.defaultifempty import default_if_empty
        return default_if_empty(default_value)(self)

    def delay(self, duetime):
        """Time shifts the observable sequence by duetime. The relative
        time intervals between the values are preserved.

        Examples:
            >>> res = rx.Observable.delay(datetime())
            >>> res = rx.Observable.delay(5000)

        Args:
            duetime: Absolute (specified as a datetime object) or
                relative time (specified as an integer denoting
                milliseconds) by which to shift the observable sequence.

        Returns:
            Time-shifted observable sequence.
        """
        from ..operators.observable.delay import delay
        return delay(duetime)(self)

    def delay_subscription(self, duetime: Union[datetime, int]) -> 'ObservableBase':
        """Time shifts the observable sequence by delaying the
        subscription.

        Example:
            >>> res = source.delay_subscription(5000) # 5s

        Args:
            duetime: Absolute or relative time to perform the
            subscription at.

        Returns:
            Time-shifted observable sequence.
        """
        from ..operators.observable.delaysubscription import delay_subscription
        return delay_subscription(self, duetime)

    def delay_with_selector(self, subscription_delay=None, delay_duration_mapper=None
                            ) -> 'ObservableBase':
        """Time shifts the observable sequence based on a subscription
        delay and a delay mapper function for each element.

        Examples:
            # with mapper only
            >>> res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
            # with delay and mapper
            >>> res = source.delay_with_selector(Observable.timer(2000), lambda x: Observable.timer(x))

        Args:
            subscription_delay: Sequence indicating the delay for the
                subscription to the source.
            delay_duration_mapper: Selector function to retrieve a
                sequence indicating the delay for each given element.

        Returns:
            Time-shifted observable sequence.
        """
        from ..operators.observable.delaywithselector import delay_with_selector
        return delay_with_selector(self, subscription_delay, delay_duration_mapper)

    def dematerialize(self) -> 'ObservableBase':
        """Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Returns:
            An observable sequence exhibiting the behavior corresponding
            to the source sequence's notification values.
        """
        from ..operators.observable.dematerialize import dematerialize
        return dematerialize(self)

    def distinct(self, key_mapper=None, comparer=None) -> 'ObservableBase':
        """Returns an observable sequence that contains only distinct
        elements according to the key_mapper and the comparer. Usage
        of this operator should be considered carefully due to the
        maintenance of an internal lookup structure which can grow
        large.

        Examples:
            >>> res = obs = xs.distinct()
            >>> obs = xs.distinct(lambda x: x.id)
            >>> obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)

        Args:
            key_mapper: A function to compute the comparison key for
                each element.
            comparer: Used to compare items in the collection.

        Returns:
            An observable sequence only containing the distinct
            elements, based on a computed key value, from the source
            sequence.
        """
        from ..operators.observable.distinct import distinct
        return distinct(key_mapper, comparer)(self)

    def distinct_until_changed(self, key_mapper=None, comparer=None) -> 'ObservableBase':
        """Returns an observable sequence that contains only distinct
        contiguous elements according to the key_mapper and the
        comparer.

        1 - obs = observable.distinct_until_changed()
        2 - obs = observable.distinct_until_changed(lambda x: x.id)
        3 - obs = observable.distinct_until_changed(lambda x: x.id, lambda x, y: x == y)

        key_mapper -- [Optional] A function to compute the comparison
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
        return distinct_until_changed(self, key_mapper, comparer)

    def do(self, observer: typing.Observer) -> 'ObservableBase':
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
        return do(self, observer)

    def do_action(self, on_next=None, on_error=None, on_completed=None) -> 'ObservableBase':
        """Invokes an action for each element in the observable sequence
        and invokes an action on graceful or exceptional termination of
        the observable sequence. This method can be used for debugging,
        logging, etc. of query behavior by intercepting the message
        stream to run arbitrary actions for messages on the pipeline.

        1 - observable.do_action(send)
        2 - observable.do_action(on_next, on_error)
        3 - observable.do_action(on_next, on_error, on_completed)

        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke on exceptional termination
            of the observable sequence.
        on_completed -- [Optional] Action to invoke on graceful termination
            of the observable sequence.

        Returns the source sequence with the side-effecting behavior
        applied.
        """
        from ..operators.observable.do import do_action
        return do_action(on_next, on_error, on_completed)(self)

    def do_finally(self, finally_action: Callable) -> 'ObservableBase':
        """Invokes an action after an on_complete(), on_error(), or disposal
        event occurs.

        This can be helpful for debugging, logging, and other side effects
        when completion, an error, or disposal terminates an operation.

        Note this operator will strive to execute the finally_action once,
        and prevent any redudant calls

        Args:
            finally_action -- Action to invoke after on_complete, on_error,
            or disposal is called
        """
        from ..operators.observable.do import do_finally
        return do_finally(finally_action)(self)

    def do_while(self, condition: Predicate) -> 'ObservableBase':
        """Repeats source as long as condition holds emulating a do while loop.

        Keyword arguments:
        condition -- The condition which determines if the source
            will be repeated.

        Returns an observable sequence which is repeated as long as the
        condition holds.
        """
        from ..operators.observable.dowhile import do_while
        return do_while(condition)(self)

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
        return element_at(index)(self)

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
        return element_at_or_default(index, default_value)(self)

    def exclusive(self) -> 'ObservableBase':
        """Performs a exclusive waiting for the first to finish before
        subscribing to another observable. Observables that come in between
        subscriptions will be dropped on the floor.

        Returns an exclusive observable with only the results that
        happen when subscribed.
        """
        from ..operators.observable.exclusive import exclusive
        return exclusive(self)

    def expand(self, mapper: Mapper) -> 'ObservableBase':
        """Expands an observable sequence by recursively invoking
        mapper.

        mapper -- Selector function to invoke for each produced
            element, resulting in another sequence to which the mapper
            will be invoked recursively again.

        Returns an observable sequence containing all the elements
        produced by the recursive expansion.
        """
        from ..operators.observable.expand import expand
        return expand(self, mapper)

    def filter(self, predicate: Predicate = None):
        """Filters the elements of an observable sequence based on a predicate
        by incorporating the element's index.

        1 - source.filter(lambda value: value < 10)

        Keyword arguments:
        source -- Observable sequence to filter.
        predicate --  A function to test each source element for a
            condition.

        Returns an observable sequence that contains elements from the input
        sequence that satisfy the condition.
        """
        from ..operators.observable.filter import filter as _filter
        return ObservableBase(_filter(predicate)(self))

    def filteri(self, predicate: PredicateIndexed = None):
        """Filters the elements of an observable sequence based on a predicate
        by incorporating the element's index.

        1 - source.filter(lambda value, index: index < 10)

        Keyword arguments:
        source -- Observable sequence to filter.
        predicate -- A function to test each source element for a
            condition; the second parameter of the function represents the
            index of the source element.

        Returns an observable sequence that contains elements from the input
        sequence that satisfy the condition.
        """
        from ..operators.observable.filter import filteri
        return ObservableBase(filteri(predicate)(self))

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
        return finally_action(self, action)

    def find(self, predicate: Predicate) -> 'ObservableBase':
        """Searches for an element that matches the conditions defined by the
        specified predicate, and returns the first occurrence within the entire
        Observable sequence.

        Args:
            predicate -- The predicate that defines the conditions of
                the element to search for.

        Returns:
            An Observable sequence with the first element that matches
            the conditions defined by the specified predicate, if found
            otherwise, None.
        """
        from ..operators.observable.find import find
        return find(predicate)(self)

    def find_index(self, predicate: Predicate) -> 'ObservableBase':
        """Searches for an element that matches the conditions defined by
        the specified predicate, and returns an Observable sequence with the
        zero-based index of the first occurrence within the entire
        Observable sequence.

        Keyword Arguments:
        predicate -- The predicate that defines the conditions of the
            element to search for.

        Returns an observable {Observable} sequence with the zero-based index of
        the first occurrence of an element that matches the conditions defined
        by match, if found; otherwise, -1.
        """
        from ..operators.observable.findindex import find_index
        source = self
        return find_index(source, predicate)

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
        return first(predicate)(self)

    def first_or_default(self, predicate=None, default_value=None) -> 'ObservableBase':
        """Returns the first element of an observable sequence that
        satisfies the condition in the predicate, or a default value if
        no such element exists.

        Examples:
            >>> res = source.first_or_default()
            >>> res = source.first_or_default(lambda x: x > 3)
            >>> res = source.first_or_default(lambda x: x > 3, 0)
            >>> res = source.first_or_default(null, 0)

        Args:
            predicate -- [optional] A predicate function to evaluate for
                elements in the source sequence.
            default_value -- [Optional] The default value if no such
                element exists.  If not specified, defaults to None.

        Returns:
            An observable sequence containing the first element in
            the observable sequence that satisfies the condition in the
            predicate, or a default value if no such element exists.
        """
        from ..operators.observable.firstordefault import first_or_default
        return first_or_default(predicate, default_value)(self)

    def flat_map(self,
                 mapper: Mapper = None,
                 result_mapper: Callable[[Any, Any], Any] = None,
                 ) -> 'ObservableBase':
        """One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.

            >>> source.flat_map(lambda x: Observable.range(0, x))

        Or:
        Projects each element of an observable sequence to an observable
        sequence, invokes the result mapper for the source element and each
        of the corresponding inner sequence's elements, and merges the results
        into one observable sequence.

            >>> source.flat_map(lambda x: Observable.range(0, x), lambda x, y: x + y)

        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.

            >>> source.flat_map(Observable.of(1, 2, 3))

        Args:
            mapper -- A transform function to apply to each element or an
                observable sequence to project each element from the source
                sequence onto.
            result_mapper -- [Optional] A transform function to apply to each
                element of the intermediate sequence.

        Returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence
        elements and their corresponding source element to a result element.
        """
        from ..operators.observable.flatmap import flat_map
        return flat_map(mapper, result_mapper)(self)

    def flat_mapi(self,
                  mapper_indexed: MapperIndexed = None,
                  result_mapper_indexed: Callable[[Any, Any, int], Any] = None
                  ) -> 'ObservableBase':
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

        1 - source.flat_mapi(lambda x, i: Observable.range(0, x), lambda x, y, i: x + y)

        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.

        1 - source.flat_mapi(Observable.of(1, 2, 3))

        Keyword arguments:
        mapper -- A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.
        result_mapper -- [Optional] A transform function to apply to each
            element of the intermediate sequence.

        Returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence
        elements and their corresponding source element to a result element.
        """
        from ..operators.observable.flatmap import flat_mapi
        return flat_mapi(mapper_indexed, result_mapper_indexed)(self)

    def group_by(self, key_mapper, element_mapper=None) -> 'ObservableBase':
        """Groups the elements of an observable sequence according to a
        specified key mapper function and comparer and selects the resulting
        elements by using a specified function.

        1 - observable.group_by(lambda x: x.id)
        2 - observable.group_by(lambda x: x.id, lambda x: x.name)
        3 - observable.group_by(
            lambda x: x.id,
            lambda x: x.name,
            lambda x: str(x))

        Keyword arguments:
        key_mapper -- A function to extract the key for each element.
        element_mapper -- [Optional] A function to map each source element to
            an element in an observable group.

        Returns a sequence of observable groups, each of which corresponds to a
        unique key value, containing all elements that share that same key
        value.
        """
        from ..operators.observable.groupby import group_by
        return group_by(self, key_mapper, element_mapper)

    def group_by_until(self, key_mapper, element_mapper, duration_mapper) -> 'ObservableBase':
        """Groups the elements of an observable sequence according to a
        specified key mapper function. A duration mapper function is used
        to control the lifetime of groups. When a group expires, it receives
        an OnCompleted notification. When a new element with the same key value
        as a reclaimed group occurs, the group will be reborn with a new
        lifetime request.

        1 - observable.group_by_until(
                lambda x: x.id,
                None,
                lambda : Rx.Observable.never()
            )
        2 - observable.group_by_until(
                lambda x: x.id,
                lambda x: x.name,
                lambda: Rx.Observable.never()
            )
        3 - observable.group_by_until(
                lambda x: x.id,
                lambda x: x.name,
                lambda:  Rx.Observable.never(),
                lambda x: str(x))

        Keyword arguments:
        key_mapper -- A function to extract the key for each element.
        duration_mapper -- A function to signal the expiration of a group.

        Returns a sequence of observable groups, each of which corresponds to
        a unique key value, containing all elements that share that same key
        value. If a group's lifetime expires, a new group with the same key
        value can be created once an element with such a key value is
        encountered.
        """
        from ..operators.observable.groupbyuntil import group_by_until
        return group_by_until(self, key_mapper, element_mapper, duration_mapper)

    def group_join(self, right, left_duration_mapper, right_duration_mapper,
                   result_mapper) -> 'ObservableBase':
        """Correlates the elements of two sequences based on overlapping
        durations, and groups the results.

        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_mapper -- A function to select the duration (expressed
            as an observable sequence) of each element of the left observable
            sequence, used to determine overlap.
        right_duration_mapper -- A function to select the duration (expressed
            as an observable sequence) of each element of the right observable
            sequence, used to determine overlap.
        result_mapper -- A function invoked to compute a result element for
            any element of the left sequence with overlapping elements from the
            right observable sequence. The first parameter passed to the
            function is an element of the left sequence. The second parameter
            passed to the function is an observable sequence with elements from
            the right sequence that overlap with the left sequence's element.

        Returns an observable sequence that contains result elements computed
        from source elements that have an overlapping duration.
        """
        from ..operators.observable.groupjoin import group_join
        return group_join(self, right, left_duration_mapper, right_duration_mapper,
                          result_mapper)

    def ignore_elements(self) -> 'ObservableBase':
        """Ignores all elements in an observable sequence leaving only
        the termination messages.

        Returns:
            An empty observable sequence that signals termination,
            successful or exceptional, of the source sequence.
        """
        from ..operators.observable.ignoreelements import ignore_elements
        return ignore_elements(self)

    def is_empty(self) -> 'ObservableBase':
        """Determines whether an observable sequence is empty.

        Returns:
            An observable sequence containing a single element
            determining whether the source sequence is empty.
        """

        return self.some().map(lambda b: not b)

    def join(self, right, left_duration_mapper, right_duration_mapper,
             result_mapper) -> 'ObservableBase':
        """Correlates the elements of two sequences based on overlapping
        durations.

        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_mapper -- A function to select the duration
            (expressed as an observable sequence) of each element of the
            left observable sequence, used to determine overlap.
        right_duration_mapper -- A function to select the duration
            (expressed as an observable sequence) of each element of the
            right observable sequence, used to determine overlap.
        result_mapper -- A function invoked to compute a result
            element for any two overlapping elements of the left and
            right observable sequences. The parameters passed to the
            function correspond with the elements from the left and
            right source sequences for which overlap occurs.

        Return an observable sequence that contains result elements computed
        from source elements that have an overlapping duration.
        """
        from ..operators.observable.join import join
        return join(self, right, left_duration_mapper, right_duration_mapper, result_mapper)

    def last(self, predicate=None) -> 'ObservableBase':
        """Returns the last element of an observable sequence that
        satisfies the condition in the predicate if specified, else the
        last element.

        Examples:
            >>> res = source.last()
            >>> res = source.last(lambda x: x > 3)

        Args:
            predicate: A predicate function to evaluate for elements in
            the source sequence.

        Returns:
            Sequence containing the last element in the observable
            sequence that satisfies the condition in the predicate.
        """
        from ..operators.observable.last import last
        return last(predicate)(self)

    def last_or_default(self, predicate=None, default_value=None) -> 'ObservableBase':
        """Return last or default element.

        Returns the last element of an observable sequence that
        satisfies the condition in the predicate, or a default value if
        no such element exists.

        Examples:
            >>> res = source.last_or_default()
            >>> res = source.last_or_default(lambda x: x > 3)
            >>> res = source.last_or_default(lambda x: x > 3, 0)
            >>> res = source.last_or_default(None, 0)

        Args:
            predicate: A predicate function to evaluate for elements in
                the source sequence.
            default_value: The default value if no such element exists.
                If not specified, defaults to None.

        Returns:
            Observable sequence containing the last element in the
            observable sequence that satisfies the condition in the
            predicate, or a default value if no such element exists.
        """
        from ..operators.observable.lastordefault import last_or_default
        return last_or_default(self, predicate, default_value)

    def let(self, func, *args, **kwargs) -> 'ObservableBase':
        """Returns an observable sequence that is the result of invoking
        the mapper on the source sequence, without sharing
        subscriptions. This operator allows for a fluent style of
        writing queries that use the same sequence multiple times.

        Any kwargs given will be passed through to the mapper. This
        allows for a clean syntax when composing with parameterized
        mappers.

        Args:
            mapper: Selector function which can use the source
                sequence as many times as needed, without sharing
                subscriptions to the source sequence.

        Returns:
            An observable sequence that contains the elements of a
            sequence produced by multicasting the source sequence within
            a mapper function.
        """
        from ..operators.observable.let import let
        return let(func, *args, **kwargs)(self)

    def many_select(self, mapper) -> 'ObservableBase':
        """Comonadic bind operator. Internally projects a new observable for each
        value, and it pushes each observable into the user-defined mapper function
        that projects/queries each observable into some result.

        Keyword arguments:
        mapper -- {Function} A transform function to apply to each element.
        scheduler -- {Object} [Optional] Scheduler used to execute the
            operation. If not specified, defaults to the ImmediateScheduler.

        Returns an observable sequence which results from the
        comonadic bind operation.
        """
        from ..operators.observable.manyselect import many_select
        return many_select(self, mapper)

    def map(self, mapper: Mapper) -> 'ObservableBase':
        """Project each element of an observable sequence into a new form.

        Example:
            >>> source.map(lambda value, index: value * value + index)

        Args:
            mapper: A transform function to apply to each source element;
                the second parameter of the function represents the index
                of the source element

        Returns:
            An observable sequence whose elements are the result of
            invoking the transform function on each element of the
            source.
        """

        from ..operators.observable.map import map as _map
        return ObservableBase(_map(mapper)(self))

    def mapi(self, mapper: MapperIndexed) -> 'ObservableBase':
        """Project each element of an observable sequence into a new form
        by incorporating the element's index.

        Example:
            >>> source.map(lambda value, index: value * value + index)

        Args:
            mapper: A transform function to apply to each source
                element; the second parameter of the function represents
                the index of the source element.

        Returns:
            An observable sequence whose elements are the result of
            invoking the transform function on each element of the
            source.
        """

        from ..operators.observable.map import mapi
        return ObservableBase(mapi(mapper)(self))

    def materialize(self) -> 'ObservableBase':
        """Materializes the implicit notifications of an observable sequence as
        explicit notification values.

        Returns:
            An observable sequence containing the materialized
            notification values from the source sequence.
        """
        from ..operators.observable.materialize import materialize
        return materialize(self)

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
        return merge(self, *args, max_concurrent=max_concurrent)

    def merge_all(self) -> 'ObservableBase':
        """Merges an observable sequence of observable sequences into an
        observable sequence.

        Returns the observable sequence that merges the elements of the inner
        sequences.
        """
        from ..operators.observable.merge import merge_all
        return merge_all(self)

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
        return max_(self, comparer)

    def max_by(self, key_mapper, comparer=None) -> 'ObservableBase':
        """Returns the elements in an observable sequence with the maximum
        key value according to the specified comparer.

        Example
        res = source.max_by(lambda x: x.value)
        res = source.max_by(lambda x: x.value, lambda x, y: x - y)

        Keyword arguments:
        key_mapper -- {Function} Key mapper function.
        comparer -- {Function} [Optional] Comparer used to compare key values.

        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a maximum key value.
        """
        from ..operators.observable.maxby import max_by
        return max_by(self, key_mapper, comparer)

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
        return min_(self, comparer)

    def min_by(self, key_mapper: Mapper, comparer=None) -> 'ObservableBase':
        """Returns the elements in an observable sequence with the minimum key
        value according to the specified comparer.

        Example
        res = source.min_by(lambda x: x.value)
        res = source.min_by(lambda x: x.value, lambda x, y: x - y)

        Keyword arguments:
        key_mapper -- {Function} Key mapper function.
        comparer -- {Function} [Optional] Comparer used to compare key values.

        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a minimum key value.
        """
        from ..operators.observable.minby import min_by
        return min_by(self, key_mapper, comparer)

    def multicast(self, subject=None, subject_factory=None, mapper=None) -> 'ObservableBase':
        """Multicasts the source sequence notifications through an instantiated
        subject into all uses of the sequence within a mapper function. Each
        subscription to the resulting sequence causes a separate multicast
        invocation, exposing the sequence resulting from the mapper function's
        invocation. For specializations with fixed subject types, see Publish,
        PublishLast, and Replay.

        Example:
        1 - res = source.multicast(observable)
        2 - res = source.multicast(subject_factory=lambda scheduler: Subject(),
                                mapper=lambda x: x)

        Keyword arguments:
        subject_factory -- {Function} Factory function to create an
            intermediate subject through which the source sequence's elements
            will be multicast to the mapper function.
        subject -- Subject {Subject} to push source elements into.
        mapper -- {Function} [Optional] Optional mapper function which can
            use the multicasted source sequence subject to the policies enforced
            by the created subject. Specified only if subject_factory" is a
            factory function.

        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        mapper function.
        """
        from ..operators.observable.multicast import multicast
        return multicast(self, subject, subject_factory, mapper)

    def observe_on(self, scheduler: abc.Scheduler) -> 'ObservableBase':
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
        return observe_on(self, scheduler)

    def pairwise(self) -> 'ObservableBase':
        """Returns a new observable that triggers on the second and subsequent
        triggerings of the input observable. The Nth triggering of the input
        observable passes the arguments from the N-1th and Nth triggering as a
        pair. The argument passed to the N-1th triggering is held in hidden
        internal state until the Nth triggering occurs.

        Returns an observable {Observable} that triggers on successive pairs of
        observations from the input observable as an array.
        """
        from ..operators.observable.pairwise import pairwise
        return pairwise(self)

    def partition(self, predicate: Predicate = None) -> List['ObservableBase']:
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
        return partition(predicate)(self)

    def partitioni(self, predicate: PredicateIndexed = None) -> List['ObservableBase']:
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
        from ..operators.observable.partition import partitioni
        return partitioni(predicate)(self)

    def pausable(self, pauser):
        """Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False.

        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable(pauser)

        Keyword parameters:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.

        Returns the observable {Observable} sequence which is paused based upon
        the pauser.
        """

        from ..backpressure.observableextensions import pausable
        return pausable(self, pauser)

    def pausable_buffered(self, subject):
        """Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False, and yields the values that were
        buffered while paused.

        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable_buffered(pauser)

        Keyword arguments:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.

        Returns the observable {Observable} sequence which is paused based upon
        the pauser."""

        from ..backpressure.observableextensions import pausable_buffered
        return pausable_buffered(self, subject)

    def pluck(self, key: Any) -> 'ObservableBase':
        """Retrieves the value of a specified key using dict-like access (as in
        element[key]) from all elements in the Observable sequence.

        Keyword arguments:
        key -- The key to pluck.

        Returns a new Observable {Observable} sequence of key values.

        To pluck an attribute of each element, use pluck_attr.

        """
        from ..operators.observable.pluck import pluck
        return pluck(self, key)

    def pluck_attr(self, attr: str) -> 'ObservableBase':
        """Retrieves the value of a specified property (using getattr) from
        all elements in the Observable sequence.

        Keyword arguments:
        attr -- The property to pluck.

        Returns a new Observable {Observable} sequence of property values.

        To pluck values using dict-like access (as in element[key]) on each
        element, use pluck.
        """

        from ..operators.observable.pluck import pluck_attr
        return pluck_attr(self, attr)

    def publish(self, mapper: Mapper = None) -> "ConnectableObservable":
        """Returns an observable sequence that is the result of invoking the
        mapper on a connectable observable sequence that shares a single
        subscription to the underlying sequence. This operator is a
        specialization of Multicast using a regular Subject.

        Examples:
            >>> res = source.publish()
            >>> res = source.publish(lambda x: x)

        Args:
            mapper: Selector function which can use the
                multicasted source sequence as many times as needed,
                without causing multiple subscriptions to the source
                sequence. Subscribers to the given source will receive
                all notifications of the source from the time of the
                subscription on.

        Returns:
            An observable sequence that contains the elements of a
            sequence produced by multicasting the source sequence
            within a mapper function."""

        from ..operators.observable.publish import publish
        return publish(self, mapper)

    def publish_value(self, initial_value: Any, mapper: Mapper = None) -> 'ObservableBase':
        """Returns an observable sequence that is the result of invoking the
        mapper on a connectable observable sequence that shares a single
        subscription to the underlying sequence and starts with initial_value.

        This operator is a specialization of Multicast using a BehaviorSubject.

        Example:
        res = source.publish_value(42)
        res = source.publish_value(42, lambda x: x.map(lambda y: y * y))

        Keyword arguments:
        initial_value -- Initial value received by observers upon
            subscription.
        mapper -- [Optional] Optional mapper function which can use the
            multicasted source sequence as many times as needed, without
            causing multiple subscriptions to the source sequence. Subscribers
            to the given source will receive immediately receive the initial
            value, followed by all notifications of the source from the time of
            the subscription on.

        Returns an observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
        """
        from ..operators.observable.publishvalue import publish_value
        return publish_value(self, initial_value, mapper)

    def reduce(self, accumulator: Accumulator, seed: Any = None) -> 'ObservableBase':
        """The reduce operator.

        Applies an accumulator function over an observable sequence,
        returning the result of the aggregation as a single element in
        the result sequence. The specified seed value is used as the
        initial accumulator value.

        For aggregation behavior with incremental intermediate results,
        see Observable.scan.

        Examples:
            >>> res = source.reduce(lambda acc, x: acc + x)
            >>> res = source.reduce(lambda acc, x: acc + x, 0)

        Args:
            accumulator: An accumulator function to be invoked on each element.
            seed: Optional initial accumulator value.

        Returns:
            An observable sequence containing a single element with the
            final accumulator value.
        """
        from ..operators.observable.reduce import reduce
        return reduce(self, accumulator, seed)

    aggregate = reduce

    def repeat(self, repeat_count=None) -> 'ObservableBase':
        """Repeats the observable sequence a specified number of times.
        If the repeat count is not specified, the sequence repeats
        indefinitely.

        Examples:
            >>> repeated = source.repeat()
            >>> repeated = source.repeat(42)

        Args:
            repeat_count: Number of times to repeat the sequence. If not
            provided, repeats the sequence indefinitely.

        Returns:
            The observable sequence producing the elements of the given
            sequence repeatedly."""

        from rx.internal.iterable import Iterable as CoreIterable
        from ..operators.observable.concat import concat
        from .observable import Observable
        return Observable.defer(lambda _: concat(CoreIterable.repeat(self, repeat_count)))

    def replay(self, mapper: Mapper = None, buffer_size: int = None, window: timedelta = None,
               scheduler: Scheduler = None) -> 'Union[ObservableBase, rx.core.ConnectableObservable]':
        """Returns an observable sequence that is the result of invoking
        the mapper on a connectable observable sequence that shares a
        single subscription to the underlying sequence replaying
        notifications subject to a maximum time length for the replay
        buffer.

        Note:
            This operator is a specialization of Multicast using a
            ReplaySubject.

        Example:
            >>> res = source.replay(buffer_size=3)
            >>> res = source.replay(buffer_size=3, window=500)
            >>> res = source.replay(None, 3, 500)
            >>> res = source.replay(lambda x: x.take(6).repeat(), 3, 500)

        Args:
            mapper: Selector function which can use the multicasted
                source sequence as many times as needed, without causing
                multiple subscriptions to the source sequence.
                Subscribers to the given source will receive all the
                notifications of the source subject to the specified
                replay buffer trimming policy.
            buffer_size: Maximum element count of the replay buffer.
            window: Maximum time length of the replay buffer.

        Returns:
            An observable sequence that contains the elements of a
            sequence produced by multicasting the source sequence within
            a mapper function.
        """
        from ..operators.observable.replay import replay
        return replay(self, mapper, buffer_size, window, scheduler)

    def retry(self, retry_count: int = None) -> 'ObservableBase':
        """Repeats the source observable sequence the specified number
        of times or until it successfully terminates. If the retry count
        is not specified, it retries indefinitely.

        Examples:
            >>> retried = xs.retry()
            >>> retried = xs.retry(42)

        Args:
            retry_count: Number of times to retry the sequence. If not
                provided, retry the sequence indefinitely.

        Returns:
            An observable sequence producing the elements of the given
            sequence repeatedly until it terminates successfully.
        """
        from ..operators.observable.retry import retry
        return retry(self, retry_count)

    def sample(self, interval=None, sampler=None):
        """Samples the observable sequence at each interval.

        Examples:
            >>> res = source.sample(sample_observable) # Sampler tick sequence
            >>> res = source.sample(5000) # 5 seconds

        Args:
            source: Source sequence to sample.
            interval: Interval at which to sample (specified as an
                integer denoting milliseconds).

        Returns sampled observable sequence.
        """
        from ..operators.observable.sample import sample
        return sample(self, interval, sampler)

    throttle_last = sample

    def scan(self, accumulator: Accumulator, seed: Any = None) -> 'ObservableBase':
        """Applies an accumulator function over an observable sequence
        and returns each intermediate result. The optional seed value is
        used as the initial accumulator value. For aggregation behavior
        with no intermediate results, see Observable.aggregate.

        Examples:
            >>> scanned = source.scan(lambda acc, x: acc + x)
            >>> scanned = source.scan(lambda acc, x: acc + x, 0)

        Args:
            accumulator: An accumulator function to be invoked on each
                element.
            seed: The initial accumulator value.

        Returns:
            An observable sequence containing the accumulated values.
        """
        from ..operators.observable.scan import scan
        return scan(self, accumulator, seed)

    def select_switch(self, mapper: Mapper) -> 'ObservableBase':
        """Projects each element of an observable sequence into a new
        sequence of observable sequences by incorporating the element's
        index and then transforms an observable sequence of observable
        sequences into an observable sequence producing values only from
        the most recent observable sequence.

        Keyword arguments:
        mapper -- A transform function to apply to each source
            element; the second parameter of the function represents the
            index of the source element.

        Returns an observable {Observable} sequence whose elements are
        the result of invoking the transform function on each element of
        source producing an Observable of Observable sequences and that
        at any point in time produces the elements of the most recent
        inner observable sequence that has been received.
        """
        return self.map(mapper).switch_latest()

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

        Returns an observable sequence that contains a single element
        which indicates whether both sequences are of equal length and
        their corresponding elements are equal according to the
        specified equality comparer.
        """
        from ..operators.observable.sequenceequal import sequence_equal
        return sequence_equal(self, second, comparer)

    def share(self) -> 'ObservableBase':
        """Share a single subscription among multple observers.

        Returns a new Observable that multicasts (shares) the original
        Observable. As long as there is at least one Subscriber this
        Observable will be subscribed and emitting data. When all
        subscribers have unsubscribed it will unsubscribe from the
        source Observable.

        This is an alias for Observable.publish().ref_count().
        """
        from..operators.observable.publish import share
        return share(self)

    def single(self, predicate: Predicate = None) -> 'ObservableBase':
        """The single operator.

        Returns the only element of an observable sequence that
        satisfies the condition in the optional predicate, and reports
        an exception if there is not exactly one element in the
        observable sequence.

        Examples:
            >>> res = source.single()
            >>> res = source.single(lambda x: x == 42)

        Args:
            predicate: A predicate function to evaluate for elements in
                the source sequence.

        Returns:
            An observable sequence containing the single element in the
            observable sequence that satisfies the condition in the
            predicate.
        """
        from ..operators.observable.single import single
        return single(self, predicate)

    def single_or_default(self, predicate: Predicate = None,
                          default_value: Any = None) -> 'ObservableBase':
        """The single_or_default operator.

        Returns the only element of an observable sequence that
        matches the predicate, or a default value if no such element
        exists this method reports an exception if there is more than
        one element in the observable sequence.

        Examples:
            >>> res = source.single_or_default()
            >>> res = source.single_or_default(lambda x: x == 42)
            >>> res = source.single_or_default(lambda x: x == 42, 0)
            >>> res = source.single_or_default(None, 0)

        Args:
            predicate: A predicate function to evaluate for elements in
                the source sequence.
            default_value: The default value if the index is outside the
                bounds of the source sequence.

        Returns:
            An observable sequence containing the single element in the
        observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
        """
        from ..operators.observable.singleordefault import single_or_default
        return single_or_default(self, predicate, default_value)

    def skip(self, count: int) -> 'ObservableBase':
        """The skip operator.

        Bypasses a specified number of elements in an observable
        sequence and then returns the remaining elements.

        Args:
            count: The number of elements to skip before returning the
                remaining elements.

        Returns:
            An observable sequence that contains the elements that
            occur after the specified index in the input sequence.
        """
        from ..operators.observable.skip import skip
        return skip(count, self)

    def skip_last(self, count: int) -> 'ObservableBase':
        """
        Bypasses a specified number of elements in an observable
        sequence and then returns the remaining elements.

        Args:
            count: The number of elements to skip before returning the
                remaining elements.

        Returns:
            An observable sequence that contains the elements that
            occur after the specified index in the input sequence.
        """
        from ..operators.observable.skiplast import skip_last
        return skip_last(count, self)

    def skip_last_with_time(self, duration: Union[timedelta, int]) -> 'ObservableBase':
        """
        Skips elements for the specified duration from the end of the
        observable source sequence.

        Example:
            >>> res = source.skip_last_with_time(5000)

        This operator accumulates a queue with a length enough to store
        elements received during the initial duration window. As more
        elements are received, elements older than the specified
        duration are taken from the queue and produced on the result
        sequence. This causes elements to be delayed with duration.

        Args:
            duration: Duration for skipping elements from the end of the
                sequence.

        Returns:
            An observable sequence with the elements skipped during
            the specified duration from the end of the source sequence.
        """
        from ..operators.observable.skiplastwithtime import skip_last_with_time
        return skip_last_with_time(self, duration)

    def skip_until(self, other: 'ObservableBase') -> 'ObservableBase':
        """Returns the values from the source observable sequence only
        after the other observable sequence produces a value.

        Args:
            other: The observable sequence that triggers propagation of
                elements of the source sequence.

        Returns:
            An observable sequence containing the elements of the
            source sequence starting from the point the other sequence
            triggered propagation.
        """
        from ..operators.observable.skipuntil import skip_until
        return skip_until(self, other)

    def skip_until_with_time(self, start_time: Union[datetime, int]) -> 'ObservableBase':
        """Skips elements from the observable source sequence until the
        specified start time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the start
        time.

        Examples:
            >>> res = source.skip_until_with_time(datetime);
            >>> res = source.skip_until_with_time(5000);

        Args:
            start_time: Time to start taking elements from the source
                sequence. If this value is less than or equal to
                datetime.utcnow(), no elements will be skipped.

        Returns:
            An observable sequence with the elements skipped until the
            specified start time.
        """
        from ..operators.observable.skipuntilwithtime import skip_until_with_time
        return skip_until_with_time(self, start_time)

    def skip_while(self, predicate: Callable[[Any], Any]) -> 'ObservableBase':
        """Bypasses elements in an observable sequence as long as a
        specified condition is true and then returns the remaining
        elements. The element's index is used in the logic of the
        predicate function.

        Examples:
            >>> source.skip_while(lambda value: value < 10)
            >>> source.skip_while(lambda value, index: value < 10 or index < 10)

        Args:
            predicate: A function to test each element for a condition;
            the second parameter of the function represents the index of
            the source element.

        Returns:
            An observable sequence that contains the elements from the
            input sequence starting at the first element in the linear
            series that does not pass the test specified by predicate.
        """
        from ..operators.observable.skipwhile import skip_while
        return skip_while(self, predicate)

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
        return skip_while_indexed(self, predicate)

    def skip_with_time(self, duration: Union[timedelta, int]) -> 'ObservableBase':
        """Skips elements for the specified duration from the start of
        the observable source sequence.

        Example:
            >>> res = source.skip_with_time(5000)

        Specifying a zero value for duration doesn't guarantee no
        elements will be dropped from the start of the source sequence.
        This is a side-effect of the asynchrony introduced by the
        scheduler, where the action that causes callbacks from the
        source sequence to be forwarded may not execute immediately,
        despite the zero due time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the
        duration.

        Args:
            duration: Duration for skipping elements from the start of
                the sequence.

        Returns:
            An observable sequence with the elements skipped during
            the specified duration from the start of the source
            sequence.
        """
        from ..operators.observable.skipwithtime import skip_with_time
        return skip_with_time(self, duration)

    def some(self, predicate=None) -> 'ObservableBase':
        """Determines whether some element of an observable sequence
        satisfies a condition if present, else if some items are in the
        sequence.

        Examples:
            >>> result = source.some()
            >>> result = source.some(lambda x: x > 3)

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            An observable sequence containing a single element
            determining whether some elements in the source sequence
            pass the test in the specified predicate if given, else if
            some items are in the sequence.
        """
        from ..operators.observable.some import some
        return some(predicate)(self)

    def start_with(self, *args: Any) -> 'ObservableBase':
        """Prepends a sequence of values to an observable.

        Example:
            >>> source.start_with(1, 2, 3)

        Returns:
            The source sequence prepended with the specified values.
        """
        from ..operators.observable.startswith import start_with
        return start_with(self, *args)

    def subscribe_on(self, scheduler) -> 'ObservableBase':
        """Subscribe on the specified scheduler.

        Wrap the source sequence in order to run its subscription and
        unsubscription logic on the specified scheduler. This operation
        is not commonly used; see the remarks section for more
        information on the distinction between subscribe_on and
        observe_on.

        Keyword arguments:
        scheduler -- Scheduler to perform subscription and
            unsubscription actions on.

        Returns the source sequence whose subscriptions and
        unsubscriptions happen on the specified scheduler.

        This only performs the side-effects of subscription and
        unsubscription on the specified scheduler. In order to invoke
        observer callbacks on a scheduler, use observe_on.
        """
        from ..operators.observable.subscribeon import subscribe_on
        return subscribe_on(self, scheduler)

    def sum(self, key_mapper: Mapper = None) -> 'ObservableBase':
        """Computes the sum of a sequence of values that are obtained by
        invoking an optional transform function on each element of the
        input sequence, else if not specified computes the sum on each
        item in the sequence.

        Examples:
            >>> res = source.sum()
            >>> res = source.sum(lambda x: x.value)

        Args:
            key_mapper: A transform function to apply to each element.

        Returns:
            An observable sequence containing a single element with
            the sum of the values in the source sequence.
        """
        from ..operators.observable.sum import sum as _sum
        return _sum(self, key_mapper)

    def switch_latest(self) -> 'ObservableBase':
        """Transforms an observable sequence of observable sequences
        into an observable sequence producing values only from the most
        recent observable sequence.

        Returns the observable sequence that at any point in time
        produces the elements of the most recent inner observable
        sequence that has been received.
        """
        from ..operators.observable.switchlatest import switch_latest
        return switch_latest(self)

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
        return take(count, self)

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
        return take_last(count, self)

    def take_last_buffer(self, count) -> 'ObservableBase':
        """Returns an array with the specified number of contiguous
        elements from the end of an observable sequence.

        Example:
        res = source.take_last(5)

        Description:
        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence,
        this buffer is drained on the result sequence. This causes the
        elements to be delayed.

        Keyword arguments:
        count -- Number of elements to take from the end of the source
            sequence.

        Returns an observable sequence containing a single list with the
        specified number of elements from the end of the source
        sequence.
        """
        from ..operators.observable.takelastbuffer import take_last_buffer
        return take_last_buffer(self, count)

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

        Returns an observable sequence with the elements taken during
        the specified duration from the end of the source sequence.
        """
        from ..operators.observable.takelastwithtime import take_last_with_time
        return take_last_with_time(self, duration)

    def take_until(self, other: 'ObservableBase') -> 'ObservableBase':
        """Returns the values from the source observable sequence until
        the other observable sequence produces a value.

        Keyword arguments:
        other -- Observable sequence that terminates propagation of
            elements of the source sequence.

        Returns an observable sequence containing the elements of the
        source sequence up to the point the other sequence interrupted
        further propagation.
        """
        from ..operators.observable.takeuntil import take_until
        return take_until(self, other)

    def take_until_with_time(self, end_time) -> 'ObservableBase':
        """Takes elements for the specified duration until the specified end
        time, using the specified scheduler to run timers.

        Examples:
        1 - res = source.take_until_with_time(dt, [optional scheduler])
        2 - res = source.take_until_with_time(5000, [optional scheduler])

        Keyword Arguments:
        end_time -- {Number | Date} Time to stop taking elements from the source
            sequence. If this value is less than or equal to Date(), the
            result stream will complete immediately.
        scheduler -- {Scheduler} Scheduler to run the timer on.

        Returns an observable {Observable} sequence with the elements taken
        until the specified end time.
        """
        from ..operators.observable.takeuntilwithtime import take_until_with_time
        return take_until_with_time(self, end_time)

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
        return take_while(self, predicate)

    def take_while_indexed(self, predicate: Callable[[Any, int], Any]) -> 'ObservableBase':
        """Returns elements from an observable sequence as long as a
        specified condition is true. The element's index is used in the
        logic of the predicate function.

        1 - source.take_while(lambda value, index: value < 10 or index < 10)

        Keyword arguments:
        predicate -- A function to test each element for a condition;
            the second parameter of the function represents the index of
            the source element.

        Returns an observable sequence that contains the elements from
        the input sequence that occur before the element at which the
        test no longer passes.
        """
        from ..operators.observable.takewhile import take_while_indexed
        return take_while_indexed(self, predicate)

    def take_with_time(self, duration: Union[timedelta, int]) -> 'ObservableBase':
        """Takes elements for the specified duration from the start of
        the observable source sequence.

        Example:
        res = source.take_with_time(5000)

        Description:
        This operator accumulates a queue with a length enough to store
        elements received during the initial duration window. As more
        elements are received, elements older than the specified
        duration are taken from the queue and produced on the result
        sequence. This causes elements to be delayed with duration.

        Keyword arguments:
        duration -- Duration for taking elements from the start of the
            sequence.

        Returns an observable sequence with the elements taken during
        the specified duration from the start of the source sequence.
        """
        from ..operators.observable.takewithtime import take_with_time
        return take_with_time(self, duration)

    def then_do(self, mapper: Mapper) -> 'ObservableBase':
        """Matches when the observable sequence has an available value
        and projects the value.

        mapper -- Selector that will be invoked for values in the
            source sequence.

        Returns Plan that produces the projected values, to be fed (with
        other plans) to the when operator.
        """
        from ..operators.observable.thendo import then_do
        return then_do(self, mapper)

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
        return throttle_first(self, window_duration)

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
        return throttle_with_timeout(duetime)(self)

    debounce = throttle_with_timeout

    def throttle_with_mapper(self, throttle_duration_mapper) -> 'ObservableBase':
        """Ignores values from an observable sequence which are followed
        by another value within a computed throttle duration.

        1 - res = source.throttle_with_mapper(lambda x: rx.Scheduler.timer(x+x))

        Keyword arguments:
        throttle_duration_mapper -- Selector function to retrieve a
            sequence indicating the throttle duration for each given
            element.

        Returns the throttled sequence.
        """
        from ..operators.observable.debounce import throttle_with_mapper
        return throttle_with_mapper(throttle_duration_mapper)(self)

    def on_error_resume_next(self, second) -> 'ObservableBase':
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

        from ..operators.observable.onerrorresumenext import on_error_resume_next
        return on_error_resume_next([self, second])

    def time_interval(self) -> 'ObservableBase':
        """Records the time interval between consecutive values in an
        observable sequence.

        1 - res = source.time_interval()

        Return An observable sequence with time interval information on
        values.
        """
        from ..operators.observable.timeinterval import time_interval
        return time_interval(self)

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
        return timeout(self, duetime, other)

    def timeout_with_selector(self, first_timeout=None,
                              timeout_duration_mapper=None, other=None) -> 'ObservableBase':
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
        timeout_Duration_mapper -- [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the
            current element and the next element.
        other -- [Optional] Sequence to return in case of a timeout. If
            not provided, this is set to Observable.throw().

        Returns the source sequence switching to the other sequence in
        case of a timeout.
        """
        from ..operators.observable.timeoutwithselector import timeout_with_selector
        return timeout_with_selector(self, first_timeout, timeout_duration_mapper, other)

    def timestamp(self) -> 'ObservableBase':
        """Records the timestamp for each value in an observable
        sequence.

        1 - res = source.timestamp() # produces objects with attributes
            "value" and "timestamp", where value is the original value.

        Returns an observable sequence with timestamp information on
        values.
        """
        from ..operators.observable.timestamp import timestamp
        return timestamp(self)

    def to_blocking(self) -> BlockingObservable:
        from ..operators.observable.toblocking import to_blocking
        source = self
        return to_blocking(source)

    def to_dict(self, key_mapper: Mapper,
                element_mapper: Mapper = None) -> 'ObservableBase':
        """Converts the observable sequence to a Map if it exists.

        Keyword arguments:
        key_mapper -- A function which produces the key for the
            dictionary.
        element_mapper -- [Optional] An optional function which
            produces the element for the dictionary. If not present,
            defaults to the value from the observable sequence.

        Returns an observable sequence with a single value of a
        dictionary containing the values from the observable sequence.
        """
        from ..operators.observable.todict import to_dict
        return to_dict(self, key_mapper, element_mapper)

    def to_future(self, future_ctor: Callable[[], Future] = None) -> Future:
        """Converts an existing observable sequence to a Future.

        Example:
        future = Observable.return_value(42).to_future(trollius.Future)

        With config:
        rx.config["Future"] = trollius.Future
        future = Observable.return_value(42).to_future()

        future_ctor -- [Optional] The constructor of the future.
            If not provided, it uses asyncio.Future.

        Returns a future with the last value from the observable
        sequence.
        """
        from ..operators.observable.tofuture import to_future
        return to_future(self, future_ctor)

    def to_iterable(self) -> 'ObservableBase':
        """Creates an iterable from an observable sequence.

        Returns an observable sequence containing a single element with
        a list containing all the elements of the source sequence.
        """
        from ..operators.observable.toiterable import to_iterable
        return to_iterable(self)

    def to_marbles(self, scheduler=None):
        """Convert an observable sequence into a marble diagram string

        Keyword arguments:
        scheduler -- [Optional] The scheduler used to run the the input
            sequence on.

        Returns Observable
        """
        from ..testing.marbles import to_marbles
        return to_marbles(self)

    def to_set(self) -> 'ObservableBase':
        """Converts the observable sequence to a set.

        Returns an observable sequence with a single value of a set
        containing the values from the observable sequence.
        """
        from ..operators.observable.toset import to_set
        return to_set(self)

    def window(self, window_openings=None, window_closing_mapper=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or
        more windows.

        Args:
            window_openings -- Observable sequence whose elements denote
                the creation of windows.
            window_closing_mapper -- [Optional] A function invoked to
                define the closing of each produced window. It defines the
                boundaries of the produced windows (a window is started
                when the previous one is closed, resulting in
                non-overlapping windows).

        Returns:
            An observable sequence of windows.
        """
        from ..operators.observable.window import window
        return window(self, window_openings, window_closing_mapper)

    def window_with_count(self, count, skip=None) -> 'ObservableBase':
        """Projects each element of an observable sequence into zero or
        more windows which are produced based on element count
        information.

        Examples:
            >>> xs.window_with_count(10)
            >>> xs.window_with_count(10, 1)

        Args:
            count -- Length of each window.
            skip -- [Optional] Number of elements to skip between creation
                of consecutive windows. If not specified, defaults to the
                count.

        Returns:
            An observable sequence of windows.
        """
        from ..operators.observable.windowwithcount import window_with_count
        return window_with_count(self, count, skip)

    def window_with_time(self, timespan, timeshift=None) -> 'ObservableBase':
        from ..operators.observable.windowwithtime import window_with_time
        return window_with_time(self, timespan, timeshift)

    def window_with_time_or_count(self, timespan, count) -> 'ObservableBase':
        from ..operators.observable.windowwithtimeorcount import window_with_time_or_count
        return window_with_time_or_count(timespan, count)(self)

    def with_latest_from(self, observables: Union['ObservableBase', Iterable['ObservableBase']],
                         mapper: Callable[[Any], Any]) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable
        sequence by using the mapper function only when the source
        observable sequence (the instance) produces an element. The
        other observables can be passed either as seperate arguments or
        as a list.

        1 - obs = observable.with_latest_from(obs, lambda o1, o2: o1 + o2)

        2 - obs = observable.with_latest_from([obs1, obs2],
                                              lambda o1, o2, o3: o1 + o2 + o3)

        Returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
        """
        from ..operators.observable.withlatestfrom import with_latest_from
        if isinstance(observables, typing.Observable):
            observables = [observables]

        sources = [self] + list(observables)
        return with_latest_from(sources, mapper)

    def zip(self, *args: 'Union[Iterable[Any], ObservableBase]',
            result_mapper: Mapper = None) -> 'ObservableBase':
        """Merges the specified observable sequences into one observable
        sequence by using the mapper function whenever all of the
        observable sequences or an array have produced an element at a
        corresponding index.

        The last element in the arguments must be a function to invoke
        for each series of elements at corresponding indexes in the
        sources.

        Examples:
            >>> res = obs1.zip(obs2, result_mapper=fn)
            >>> res = x1.zip([1,2,3], result_mapper=fn)

        Args:
            args -- Observable sources to zip together with self.
            result_mapper -- Selector function that produces an element
                whenever all of the observable sequences have produced
                an element at a corresponding index

        Returns:
            An observable sequence containing the result of
            combining elements of the sources using the specified result
            mapper function.
        """
        from ..operators.observable.zip import zip as _zip
        return _zip(self, *args, result_mapper=result_mapper)
