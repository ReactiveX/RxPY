import types
from datetime import datetime
from typing import Callable, Any, Iterable, Union, Generic, TypeVar
from abc import abstractmethod
from asyncio.futures import Future

from rx import config
from .anonymousobserver import AnonymousObserver
from . import bases

T_out = TypeVar('T_out', covariant=True)


class Observable(Generic[T_out], bases.Observable):
    """Represents a push-style collection."""

    def __init__(self):
        self.lock = config["concurrency"].RLock()

        # Deferred instance method assignment:
        # TODO will be removed when extensionmethods are gone
        for name, method in self._methods:
            setattr(self, name, types.MethodType(method, self))

    def __add__(self, other):
        """Pythonic version of concat

        Example:
        zs = xs + ys
        Returns self.concat(other)"""
        from ..operators.observable.concat import concat
        return concat(self, other)

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

    def subscribe(self, observer=None, scheduler=None):
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

    def subscribe_callbacks(self, send=None, throw=None, close=None, scheduler=None):
        """Subscribe callbacks to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe_callbacks(send)
        3 - source.subscribe_callbacks(send, throw)
        4 - source.subscribe_callbacks(send, throw, close)

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

    def as_observable(self) -> 'Observable':
        """Hides the identity of an observable sequence.

        Returns an observable sequence that hides the identity of the
        source sequence.
        """
        from ..operators.observable.asobservable import as_observable
        source = self
        return as_observable(source)

    def combine_latest(self, observables: Union['Observable', Iterable['Observable']],
                       selector: Callable[[Any], Any]) -> 'Observable':
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
        if isinstance(observables, Observable):
            observables = [observables]

        args = [self] + list(observables)
        return combine_latest(args, selector)

    def concat(self, *args: 'Observable') -> 'Observable':
        """Concatenates all the observable sequences. This takes in either an
        array or variable arguments to concatenate.

        1 - concatenated = xs.concat(ys, zs)

        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        from ..operators.observable.concat import concat
        source = self
        return concat(source, *args)

    def concat_all(self) -> 'Observable':
        """Concatenates an observable sequence of observable sequences.

        Returns an observable sequence that contains the elements of each
        observed inner sequence, in sequential order.
        """
        return self.merge(1)

    def concat_map(self, mapper: Callable[[Any], Any]) -> 'Observable':
        """Maps each emission to an Observable and fires its emissions.
        It will only fire each resulting Observable sequentially.
        The next derived Observable will not start its emissions until
        the current one calls close
        """
        return self.map(mapper).concat_all()

    @classmethod
    def create(cls, subscribe) -> 'Observable':
        from ..operators.observable.create import create
        return create(subscribe)

    create_with_disposable = create

    @classmethod
    def defer(cls, observable_factory: Callable[[Any], 'Observable']) -> 'Observable':
        """Returns an observable sequence that invokes the specified
        factory function whenever a new observer subscribes.

        Example:
        1 - res = rx.Observable.defer(lambda: rx.Observable.from_([1,2,3]))

        Keyword arguments:
        :param types.FunctionType observable_factory: Observable factory
        function to invoke for each observer that subscribes to the
        resulting sequence.

        :returns: An observable sequence whose observers trigger an
        invocation of the given observable factory function.
        :rtype: Observable
        """
        from ..operators.observable.defer import defer
        return defer(observable_factory)

    def do_while(self, condition: Callable[[Any], bool]) -> 'Observable':
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

    @classmethod
    def empty(cls) -> 'Observable':
        """Returns an empty observable sequence.

        1 - res = rx.Observable.empty()

        scheduler -- Scheduler to send the termination call on.

        Returns an observable sequence with no elements.
        """
        from ..operators.observable.empty import empty
        return empty()

    def filter(self, predicate: Callable[[Any], bool]) -> 'Observable':
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

    def filter_indexed(self, predicate: Callable[[Any, int], bool]) -> 'Observable':
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

    def flat_map(self, selector: Callable, result_selector: Callable=None) -> 'Observable':
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

    @classmethod
    def from_callable(cls, supplier: Callable) -> 'Observable':
        """Returns an observable sequence that contains a single element
        generate from a supplier, using the specified scheduler to send
        out observer messages.

        example
        res = rx.Observable.from_callable(lambda: calculate_value())
        res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error

        Keyword arguments:
        supplier -- Single element in the resulting observable sequence.
        scheduler -- [Optional] Scheduler to send the single element on. If
            not specified, defaults to Scheduler.immediate.

        Returns an observable sequence containing the single specified
        element derived from the supplier
        """
        from ..operators.observable.returnvalue import from_callable
        return from_callable(supplier)

    @classmethod
    def from_future(cls, future: Union['Observable', Future]) -> 'Observable':
        """Converts a Future to an Observable sequence

        Keyword Arguments:
        future -- A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

        Returns an Observable sequence which wraps the existing future
        success and failure.
        """
        from ..operators.observable.fromfuture import from_future
        return from_future(future)

    @classmethod
    def from_iterable(cls, iterable: Iterable) -> 'Observable':
        """Converts an array to an observable sequence.

        1 - res = rx.Observable.from_iterable([1,2,3])

        Keyword arguments:
        iterable - An python iterable

        Returns the observable sequence whose elements are pulled from
            the given enumerable sequence.
        """
        from ..operators.observable.fromiterable import from_iterable
        return from_iterable(iterable)

    from_ = from_iterable
    from_list = from_iterable

    def map(self, mapper: Callable[[Any], Any]) -> 'Observable':
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

    def map_indexed(self, mapper: Callable[[Any, int], Any]) -> 'Observable':
        from ..operators.observable.map import map_indexed
        source = self
        return map_indexed(mapper, source)

    @classmethod
    def never(cls) -> 'Observable':
        """Returns a non-terminating observable sequence.

        Such a sequence can be used to denote an infinite duration (e.g.
        when using reactive joins).

        Returns an observable sequence whose observers will never get
        called.
        """
        from ..operators.observable.never import never
        return never()

    @classmethod
    def range(cls, start: int, stop: int=None, step: int=None) -> 'Observable':
        """Generates an observable sequence of integral numbers within a
        specified range, using the specified scheduler to send out observer
        messages.

        1 - res = Rx.Observable.range(10)
        2 - res = Rx.Observable.range(0, 10)
        3 - res = Rx.Observable.range(0, 10, 1)

        Keyword arguments:
        start -- The value of the first integer in the sequence.
        count -- The number of sequential integers to generate.
        scheduler -- [Optional] Scheduler to run the generator loop on. If not
            specified, defaults to Scheduler.current_thread.

        Returns an observable sequence that contains a range of sequential
        integral numbers.
        """
        from ..operators.observable.range import from_range
        return from_range(start, stop, step)

    def reduce(self, accumulator: Callable[[Any, Any], Any], seed: Any=None) -> 'Observable':
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

    @classmethod
    def return_value(cls, value) -> 'Observable':
        """Returns an observable sequence that contains a single element,
        using the specified scheduler to send out observer messages.
        There is an alias called 'just'.

        example
        res = rx.Observable.return(42)

        Keyword arguments:
        value -- Single element in the resulting observable sequence.

        Returns an observable sequence containing the single specified
        element.
        """
        from ..operators.observable.returnvalue import return_value
        return return_value(value)

    just = return_value

    def repeat(self, repeat_count=None) -> 'Observable':
        """Repeats the observable sequence a specified number of times. If the
        repeat count is not specified, the sequence repeats indefinitely.

        1 - repeated = source.repeat()
        2 - repeated = source.repeat(42)

        Keyword arguments:
        repeat_count -- Number of times to repeat the sequence. If not
            provided, repeats the sequence indefinitely.

        Returns the observable sequence producing the elements of the given
        sequence repeatedly."""

        from ..operators.observable.concat import concat
        from rx.internal.iterable import Iterable as CoreIterable
        return Observable.defer(lambda _: concat(CoreIterable.repeat(self, repeat_count)))

    @staticmethod
    def repeat_value(value: Any = None, repeat_count: int = None) -> 'Observable':
        """Generates an observable sequence that repeats the given element
        the specified number of times.

        1 - res = Observable.repeat(42)
        2 - res = Observable.repeat(42, 4)

        Keyword arguments:
        value -- Element to repeat.
        repeat_count -- [Optional] Number of times to repeat the element.
            If not specified, repeats indefinitely.

        Returns an observable sequence that repeats the given element the
        specified number of times."""
        from ..operators.observable.repeat import repeat_value
        return repeat_value(value, repeat_count)

    def scan(self, accumulator: Callable[[Any, Any], Any], seed: Any=None) -> 'Observable':
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

    def select_switch(self, selector: Callable) -> 'Observable':
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

    def skip(self, count: int) -> 'Observable':
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

    def skip_last(self, count: int) -> 'Observable':
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

    def skip_while(self, predicate: Callable[[Any], Any]) -> 'Observable':
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

    def skip_while_indexed(self, predicate: Callable[[Any, int], Any]) -> 'Observable':
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

    def start_with(self, *args: Any) -> 'Observable':
        """Prepends a sequence of values to an observable.

        1 - source.start_with(1, 2, 3)

        Returns the source sequence prepended with the specified values.
        """
        from ..operators.observable.startswith import start_with
        source = self
        return start_with(source, *args)

    def switch_latest(self) -> 'Observable':
        """Transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.

        :returns: The observable sequence that at any point in time produces the
        elements of the most recent inner observable sequence that has been
        received.
        :rtype: Observable
        """
        from ..operators.observable.switchlatest import switch_latest
        sources = self
        return switch_latest(sources)

    def take(self, count: int) -> 'Observable':
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

    def take_last(self, count: int) -> 'Observable':
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

    def time_interval(self) -> 'Observable':
        """Records the time interval between consecutive values in an
        observable sequence.

        1 - res = source.time_interval()

        Return An observable sequence with time interval information on
        values.
        """
        from ..operators.observable.timeinterval import time_interval
        source = self
        return time_interval(source)

    def timeout(self, duetime: Union[int, datetime], other: 'Observable' = None) -> 'Observable':
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

        Returns the source sequence switching to the other sequence in case
            of a timeout.
        """
        from ..operators.observable.timeout import timeout
        source = self
        return timeout(source, duetime, other)

    def timestamp(self) -> 'Observable':
        """Records the timestamp for each value in an observable sequence.

        1 - res = source.timestamp() # produces objects with attributes "value" and
            "timestamp", where value is the original value.

        Returns an observable sequence with timestamp information on values.
        """
        from ..operators.observable.timestamp import timestamp
        source = self
        return timestamp(source)

    def to_iterable(self) -> 'Observable':
        """Creates an iterable from an observable sequence.

        Returns an observable sequence containing a single element with a list
        containing all the elements of the source sequence.
        """
        from ..operators.observable.toiterable import to_iterable
        source = self
        return to_iterable(source)

    def while_do(self, condition: Callable[[Any], bool]) -> 'Observable':
        """Repeats source as long as condition holds emulating a while loop.

        Keyword arguments:
        condition -- The condition which determines if the source will be
            repeated.

        Returns an observable sequence which is repeated as long as the
            condition holds.
        """
        from ..operators.observable.whiledo import while_do
        source = self
        return while_do(condition, source)

    def with_latest_from(self, observables: Union['Observable', Iterable['Observable']],
                         selector: Callable[[Any], Any]) -> 'Observable':
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
        if isinstance(observables, Observable):
            observables = [observables]

        sources = [self] + list(observables)
        return with_latest_from(sources, selector)
