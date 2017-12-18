from typing import Any, Callable, Union, Iterable
from asyncio.futures import Future

from .observablebase import ObservableBase

class Observable:
    """Observable creation methods.

    This class is a container of static Observable creation methods.
    """

    @staticmethod
    def amb(*args) -> ObservableBase:
        """Propagates the observable sequence that reacts first.

        E.g. winner = Observable.amb(xs, ys, zs)

        Returns an observable sequence that surfaces any of the given
        sequences, whichever reacted first.
        """
        from ..operators.observable.amb import amb
        return amb(*args)

    @staticmethod
    def case(selector, sources, default_source=None) -> ObservableBase:
        """Uses selector to determine which source in sources to use.

        Example:
        1 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 })
        2 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 }, obs0)

        Keyword arguments:
        selector -- The function which extracts the value for to test in a
            case statement.
        sources -- An object which has keys which correspond to the case
            statement labels.
        default_source -- The observable sequence or Future that will be run
            if the sources are not matched. If this is not provided, it
            defaults to rx.Observabe.empty.

        Returns an observable sequence which is determined by a case statement.
        """
        from ..operators.observable.case import case
        return case(selector, sources, default_source)

    switch_case = case

    @staticmethod
    def catch_exception(*args):
        """Continues an observable sequence that is terminated by an
        exception with the next observable sequence.

        1 - res = Observable.catch_exception(xs, ys, zs)
        2 - res = Observable.catch_exception([xs, ys, zs])

        Returns an observable sequence containing elements from consecutive
        source sequences until a source sequence terminates successfully.
        """
        from ..operators.observable.catch import catch_exception_
        return catch_exception_(*args)

    @staticmethod
    def create(subscribe) -> ObservableBase:
        from ..operators.observable.create import create
        return create(subscribe)

    @staticmethod
    def defer(observable_factory: Callable[[Any], ObservableBase]) -> ObservableBase:
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

    @staticmethod
    def empty() -> ObservableBase:
        """Returns an empty observable sequence.

        1 - res = rx.Observable.empty()

        scheduler -- Scheduler to send the termination call on.

        Returns an observable sequence with no elements.
        """
        from ..operators.observable.empty import empty
        return empty()

    @staticmethod
    def from_callable(supplier: Callable) -> ObservableBase:
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

    @staticmethod
    def from_future(future: Union[ObservableBase, Future]) -> ObservableBase:
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

    @staticmethod
    def from_iterable(iterable: Iterable, delay=None) -> ObservableBase:
        """Converts an array to an observable sequence.

        1 - res = rx.Observable.from_iterable([1,2,3])

        Keyword arguments:
        iterable - An python iterable

        Returns the observable sequence whose elements are pulled from
            the given enumerable sequence.
        """
        from ..operators.observable.fromiterable import from_iterable
        return from_iterable(iterable, delay)

    from_ = from_iterable
    from_list = from_iterable

    @staticmethod
    def interval(period) -> ObservableBase:
        """Returns an observable sequence that produces a value after each
        period.

        Example:
        1 - res = rx.Observable.interval(1000)

        Keyword arguments:
        period -- Period for producing the values in the resulting sequence
            (specified as an integer denoting milliseconds).

        Returns an observable sequence that produces a value after each period.
        """
        from ..operators.observable.interval import interval
        return interval(period)

    @staticmethod
    def merge(*args):
        """Merges all the observable sequences into a single observable
        sequence.

        1 - merged = rx.Observable.merge(xs, ys, zs)
        2 - merged = rx.Observable.merge([xs, ys, zs])

        Returns the observable sequence that merges the elements of the
        observable sequences.
        """
        from ..operators.observable.merge import merge_
        return merge_(*args)

    @staticmethod
    def never() -> ObservableBase:
        """Returns a non-terminating observable sequence.

        Such a sequence can be used to denote an infinite duration (e.g.
        when using reactive joins).

        Returns an observable sequence whose observers will never get
        called.
        """
        from ..operators.observable.never import never
        return never()

    @staticmethod
    def of(*args) -> ObservableBase:
        """This method creates a new Observable instance with a variable number
        of arguments, regardless of number or type of the arguments.

        Example:
        res = rx.Observable.of(1,2,3)

        Returns the observable sequence whose elements are pulled from the given
        arguments
        """
        from ..operators.observable.of import of
        return of(*args)

    @staticmethod
    def range(start: int, stop: int=None, step: int=None) -> ObservableBase:
        """Generates an observable sequence of integral numbers within a
        specified range, using the specified scheduler to send out observer
        messages.

        1 - res = rx.Observable.range(10)
        2 - res = rx.Observable.range(0, 10)
        3 - res = rx.Observable.range(0, 10, 1)

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

    @staticmethod
    def return_value(value) -> ObservableBase:
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

    @staticmethod
    def repeat_value(value: Any = None, repeat_count: int = None) -> ObservableBase:
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

    @staticmethod
    def throw(exception: Exception) -> ObservableBase:
        """Returns an observable sequence that terminates with an exception,
        using the specified scheduler to send out the single OnError message.

        1 - res = rx.Observable.throw(Exception('Error'))

        Keyword arguments:
        exception -- An object used for the sequence's termination.

        Returns the observable sequence that terminates exceptionally with the
        specified exception object.
        """
        from ..operators.observable.throw import throw
        return throw(exception)

    @staticmethod
    def timer(duetime, period=None) -> ObservableBase:
        """Returns an observable sequence that produces a value after duetime
        has elapsed and then after each period.

        1 - res = Observable.timer(datetime(...))
        2 - res = Observable.timer(datetime(...), 1000)

        5 - res = Observable.timer(5000)
        6 - res = Observable.timer(5000, 1000)

        Keyword arguments:
        duetime -- Absolute (specified as a Date object) or relative time
            (specified as an integer denoting milliseconds) at which to produce
            the first value.</param>
        period -- [Optional] Period to produce subsequent values (specified as
            an integer denoting milliseconds), or the scheduler to run the
            timer on. If not specified, the resulting timer is not recurring.

        Returns an observable sequence that produces a value after due time has
        elapsed and then each period.
        """
        from ..operators.observable.timer import timer
        return timer(duetime, period)

    @staticmethod
    def when(*args) -> ObservableBase:
        """Joins together the results from several patterns.

        args -- A series of plans (specified as a list of as a series of
            arguments) created by use of the Then operator on patterns.

        Returns Observable sequence with the results form matching several
        patterns.
        """
        from ..operators.observable.when import when
        return when(*args)

    @staticmethod
    def while_do(condition: Callable[[Any], bool], source: ObservableBase) -> ObservableBase:
        """Repeats source as long as condition holds emulating a while
        loop.

        Keyword arguments:
        condition -- The condition which determines if the source will be
            repeated.

        Returns an observable sequence which is repeated as long as the
            condition holds.
        """
        from ..operators.observable.whiledo import while_do
        return while_do(condition, source)
