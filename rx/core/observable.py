import types
from typing import Callable, Any, Iterable
from abc import abstractmethod

from rx import config
from rx.concurrency import current_thread_scheduler

from . import Observer, Disposable, bases
from .anonymousobserver import AnonymousObserver
from .autodetachobserver import AutoDetachObserver
from . import Scheduler


class Observable(bases.Observable):
    """Represents a push-style collection."""

    def __init__(self):
        self.lock = config["concurrency"].RLock()

        # Deferred instance method assignment: TODO will be removed when extensionmethods are gone
        for name, method in self._methods:
            setattr(self, name, types.MethodType(method, self))

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

    @classmethod
    def create(cls, subscribe):
        from ..operators.observable.create import create
        return create(subscribe)

    create_with_disposable = create

    def as_observable(self) -> "Observable":
        """Hides the identity of an observable sequence.

        :returns: An observable sequence that hides the identity of the source
            sequence.
        :rtype: Observable
        """
        from ..operators.observable.asobservable import as_observable
        source = self
        return as_observable(source)

    @classmethod
    def empty(cls):
        """Returns an empty observable sequence.

        1 - res = rx.Observable.empty()

        scheduler -- Scheduler to send the termination call on.

        Returns an observable sequence with no elements.
        """
        from ..operators.observable.empty import empty
        return empty()

    def filter(self, predicate: Callable[[Any], bool]) -> "Observable":
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

    def filter_indexed(self, predicate: Callable[[Any, int], bool]) -> "Observable":
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

    @classmethod
    def from_callable(cls, supplier: Callable) -> "Observable":
        """Returns an observable sequence that contains a single element generate from a supplier,
        using the specified scheduler to send out observer messages.

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
    def from_iterable(cls, iterable: Iterable):
        """Converts an array to an observable sequence, using an optional
        scheduler to enumerate the array.

        1 - res = rx.Observable.from_iterable([1,2,3])
        2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)

        Keyword arguments:
        :param Observable cls: Observable class
        :param Scheduler scheduler: [Optional] Scheduler to run the
            enumeration of the input sequence on.

        :returns: The observable sequence whose elements are pulled from the
            given enumerable sequence.
        :rtype: Observable
        """
        from ..operators.observable.fromiterable import from_iterable
        return from_iterable(iterable)

    from_ = from_iterable
    from_list = from_iterable

    def map(self, mapper: Callable[[Any], Any]) -> "Observable":
        """Project each element of an observable sequence into a new form
        by incorporating the element's index.

        1 - source.map(lambda value: value * value)

        Keyword arguments:
        mapper -- A transform function to apply to each source element; the
            second parameter of the function represents the index of the
            source element.

        Returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source.
        """

        from ..operators.observable.map import map as _map
        source = self
        return _map(mapper, source)

    def map_indexed(self, mapper: Callable[[Any, int], Any]) -> "Observable":
        from ..operators.observable.map import map_indexed
        source = self
        return map_indexed(mapper, source)

    @classmethod
    def never(cls):
        """Returns a non-terminating observable sequence, which can be used to
        denote an infinite duration (e.g. when using reactive joins).

        Returns an observable sequence whose observers will never get called.
        """
        from ..operators.observable.never import never
        return never()

    @classmethod
    def return_value(cls, value) -> "Observable":
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

    def skip(self, count: int) -> "Observable":
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

    def skip_last(self, count: int) -> "Observable":
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

    def start_with(self, *args, **kwargs) -> "Observable":
        """Prepends a sequence of values to an observable.

        1 - source.start_with(1, 2, 3)

        Returns the source sequence prepended with the specified values.
        """
        from ..operators.observable.startswith import start_with
        source = self
        return start_with(source, *args, **kwargs)

    def take(self, count: int) -> "Observable":
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

    def take_last(self, count: int) -> "Observable":
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

    def to_iterable(self) -> "Observable":
        """Creates an iterable from an observable sequence.

        :returns: An observable sequence containing a single element with a list
        containing all the elements of the source sequence.
        :rtype: Observable
        """
        from ..operators.observable.toiterable import to_iterable
        source = self
        return to_iterable(source)
