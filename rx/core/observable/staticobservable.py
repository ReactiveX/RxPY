from datetime import datetime, timedelta
from typing import Any, Callable, Union, Iterable
from asyncio.futures import Future

from ..typing import Mapper
from .. import abc, typing

from .observable import Observable


class StaticObservable(typing.Observable):  # pylint: disable=W0223,R0904
    """Observable creation methods.

    This class is a container of static Observable creation methods.
    """

    @staticmethod
    def amb(*args) -> Observable:
        """Propagates the observable sequence that reacts first.

        E.g. winner = Observable.amb(xs, ys, zs)

        Returns an observable sequence that surfaces any of the given
        sequences, whichever reacted first.
        """
        from ..operators.amb import amb_ as amb
        return amb(*args)

    @staticmethod
    def case(mapper, sources, default_source=None) -> Observable:
        """Uses mapper to determine which source in sources to use.

        Example:
        1 - res = rx.Observable.case(mapper, { '1': obs1, '2': obs2 })
        2 - res = rx.Observable.case(mapper, { '1': obs1, '2': obs2 }, obs0)

        Keyword arguments:
        mapper -- The function which extracts the value for to test in
            a case statement.
        sources -- An object which has keys which correspond to the case
            statement labels.
        default_source -- The observable sequence or Future that will be
            run if the sources are not matched. If this is not provided,
            it defaults to rx.Observabe.empty.

        Returns an observable sequence which is determined by a case
        statement.
        """
        from ..operators.case import case
        return case(mapper, sources, default_source)

    switch_case = case

    @staticmethod
    def catch_exception(*args):
        """Continues an observable sequence that is terminated by an
        exception with the next observable sequence.

        1 - res = Observable.catch_exception(xs, ys, zs)
        2 - res = Observable.catch_exception([xs, ys, zs])

        Returns an observable sequence containing elements from
        consecutive source sequences until a source sequence terminates
        successfully.
        """
        from ..operators.catch import catch_exception_
        return catch_exception_(*args)

    @staticmethod
    def concat(*args: Union[Observable, Iterable[Observable]]) -> Observable:
        """Concatenates all the observable sequences.

        1 - res = Observable.concat(xs, ys, zs)
        2 - res = Observable.concat([xs, ys, zs])

        Returns an observable sequence that contains the elements of
        each given sequence, in sequential order.
        """
        from ..operators.concat import concat
        return concat(*args)

    @staticmethod
    def create(subscribe) -> Observable:
        from ..operators.create import create
        return create(subscribe)

    @staticmethod
    def defer(observable_factory: Callable[[Any], Observable]) -> Observable:
        """Returns an observable sequence that invokes the specified
        factory function whenever a new observer subscribes.

        Example:
        1 - res = rx.Observable.defer(lambda: rx.Observable.of([1,2,3]))

        Keyword arguments:
        :param types.FunctionType observable_factory: Observable factory
        function to invoke for each observer that subscribes to the
        resulting sequence.

        :returns: An observable sequence whose observers trigger an
        invocation of the given observable factory function.
        :rtype: Observable
        """
        from ..operators.defer import defer
        return defer(observable_factory)

    @staticmethod
    def for_in(values: Iterable,
               result_mapper: Callable[[Any], Observable]) -> Observable:
        """Concatenates the observable sequences obtained by running the
        specified result mapper for each element in source.

        Keyword arguments:
        values -- A list of values to turn into an observable
            sequence.
        result_mapper -- A function to apply to each item in the
            values list to turn it into an observable sequence.
        Returns an observable sequence from the concatenated
        observable sequences.
        """

        from ..operators.forin import for_in
        return for_in(values, result_mapper)

    @staticmethod
    def from_callable(supplier: Callable) -> Observable:
        """Returns an observable sequence that contains a single element
        generate from a supplier.

        example
        res = rx.Observable.from_callable(lambda: calculate_value())
        res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error

        Keyword arguments:
        supplier -- Single element in the resulting observable sequence.

        Returns an observable sequence containing the single specified
        element derived from the supplier
        """
        from ..operators.returnvalue import from_callable
        return from_callable(supplier)

    @staticmethod
    def from_callback(func: Callable, mapper: Mapper = None) -> "Callable[[...], Observable]":
        """Converts a callback function to an observable sequence.

        Keyword arguments:
        func -- Function with a callback as the last parameter to
            convert to an Observable sequence.
        mapper -- [Optional] A mapper which takes the arguments
            from the callback to produce a single item to yield on next.

        Returns a function, when executed with the required parameters
        minus the callback, produces an Observable sequence with a
        single value of the arguments to the callback as a list.
        """
        from ..operators.fromcallback import from_callback
        return from_callback(func, mapper)

    @staticmethod
    def from_future(future: Union[Observable, Future]) -> Observable:
        """Converts a Future to an Observable sequence

        Keyword Arguments:
        future -- A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

        Returns an Observable sequence which wraps the existing future
        success and failure.
        """
        from ..operators.fromfuture import from_future
        return from_future(future)

    @staticmethod
    def from_marbles(string: str) -> Observable:
        """Convert a marble diagram string to an observable sequence,
        using an optional scheduler to enumerate the events.

        Special characters:
        - = Timespan of 100 ms
        x = on_error()
        | = on_completed()

        All other characters are treated as an on_next() event at the given
        moment they are found on the string.

        Examples:
        1 - res = rx.Observable.from_string("1-2-3-|")
        2 - res = rx.Observable.from_string("1-(42)-3-|")
        3 - res = rx.Observable.from_string("1-2-3-x", rx.Scheduler.timeout)

        Keyword arguments:
        string -- String with marble diagram
        scheduler -- [Optional] Scheduler to run the the input sequence on.

        Returns the observable sequence whose elements are pulled from the
        given marble diagram string.
        """
        from ..testing.marbles import from_marbles
        return from_marbles(string)

    @staticmethod
    def generate(initial_state, condition, iterate, result_mapper) -> Observable:
        """Generates an observable sequence by running a state-driven
        loop producing the sequence's elements, using the specified
        scheduler to send out observer messages.

        1 - res = rx.Observable.generate(0,
            lambda x: x < 10,
            lambda x: x + 1,
            lambda x: x)

        Keyword arguments:
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning
            False).
        iterate -- Iteration step function.
        result_mapper -- Selector function for results produced in the
            sequence.

        Returns the generated sequence.
        """
        from ..operators.generate import generate
        return generate(initial_state, condition, iterate, result_mapper)

    @staticmethod
    def generate_with_relative_time(initial_state, condition, iterate,
                                    result_mapper, time_mapper) -> Observable:
        """Generates an observable sequence by iterating a state from an
        initial state until the condition fails.

        res = source.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: 500)

        Keyword arguments:
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning
            false).
        iterate -- Iteration step function.
        result_mapper -- Selector function for results produced in the
            sequence.
        time_mapper -- Time mapper function to control the speed of
            values being produced each iteration, returning integer
            values denoting milliseconds.

        Returns the generated sequence.
        """
        from ..operators.generatewithrelativetime import generate_with_relative_time
        return generate_with_relative_time(initial_state, condition, iterate, result_mapper, time_mapper)

    @staticmethod
    def if_then(condition: Callable[[], bool], then_source: Observable,
                else_source: Observable = None) -> Observable:
        """Determines whether an observable collection contains values.

        Example:
        1 - res = rx.Observable.if(condition, obs1)
        2 - res = rx.Observable.if(condition, obs1, obs2)

        Keyword parameters:
        condition -- The condition which determines if the then_source
            or else_source will be run.
        then_source -- The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source -- [Optional] The observable sequence or
            Promise that will be run if the condition function returns
            False. If this is not provided, it defaults to
            rx.Observable.empty

        Returns an observable sequence which is either the
        then_source or else_source.
        """
        from ..operators.ifthen import if_then
        return if_then(condition, then_source, else_source)

    @staticmethod
    def interval(period: Union[timedelta, int]) -> Observable:
        """Returns an observable sequence that produces a value after
        each period.

        Example:
        1 - res = rx.Observable.interval(1000)

        Keyword arguments:
        period -- Period for producing the values in the resulting
            sequence (specified as an integer denoting milliseconds).

        Returns an observable sequence that produces a value after each
        period.
        """
        from ..operators.interval import interval
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
        from ..operators.merge import merge_
        return merge_(*args)

    @staticmethod
    def never() -> Observable:
        """Returns a non-terminating observable sequence.

        Such a sequence can be used to denote an infinite duration (e.g.
        when using reactive joins).

        Returns an observable sequence whose observers will never get
        called.
        """
        from ..operators.never import never
        return never()

    @staticmethod
    def of(*args) -> Observable:
        """This method creates a new Observable instance with a variable
        number of arguments, regardless of number or type of the arguments.

        Example:
        res = rx.Observable.of(1,2,3)

        Returns the observable sequence whose elements are pulled from
        the given arguments
        """
        from ..operators.of import of
        return of(*args)

    @staticmethod
    def range(start: int, stop: int = None, step: int = None) -> Observable:
        """Generates an observable sequence of integral numbers within a
        specified range.

        1 - res = rx.Observable.range(10)
        2 - res = rx.Observable.range(0, 10)
        3 - res = rx.Observable.range(0, 10, 1)

        Keyword arguments:
        start -- The value of the first integer in the sequence.
        count -- The number of sequential integers to generate.

        Returns an observable sequence that contains a range of
        sequential integral numbers.
        """
        from ..operators.range import from_range
        return from_range(start, stop, step)

    @staticmethod
    def return_value(value) -> Observable:
        """Returns an observable sequence that contains a single
        element. There is an alias called 'just'.

        example
        res = rx.Observable.return_value(42)

        Keyword arguments:
        value -- Single element in the resulting observable sequence.

        Returns an observable sequence containing the single specified
        element.
        """
        from ..operators.returnvalue import return_value
        return return_value(value)

    just = return_value

    @staticmethod
    def repeat_value(value: Any = None, repeat_count: int = None) -> Observable:
        """Generates an observable sequence that repeats the given element
        the specified number of times.

        1 - res = Observable.repeat(42)
        2 - res = Observable.repeat(42, 4)

        Keyword arguments:
        value -- Element to repeat.
        repeat_count -- [Optional] Number of times to repeat the
            element. If not specified, repeats indefinitely.

        Returns an observable sequence that repeats the given element
        the specified number of times."""
        from ..operators.repeat import repeat_value
        return repeat_value(value, repeat_count)

    @staticmethod
    def start(func: Callable, scheduler: abc.Scheduler = None) -> Observable:
        """Invokes the specified function asynchronously on the specified
        scheduler, surfacing the result through an observable sequence.

        Example:
        res = rx.Observable.start(lambda: pprint('hello'))
        res = rx.Observable.start(lambda: pprint('hello'), rx.Scheduler.timeout)

        Keyword arguments:
        func -- Function to run asynchronously.
        scheduler -- [Optional] Scheduler to run the function on. If not
            specified, defaults to Scheduler.timeout.

        Returns an observable sequence exposing the function's result
        value, or an exception.

        Remarks:
        The function is called immediately, not during the subscription
        of the resulting sequence. Multiple subscriptions to the
        resulting sequence can observe the function's result.
        """
        from ..operators.start import start
        return start(func, scheduler)

    @staticmethod
    def start_async(function_async: Callable) -> Observable:
        """Invokes the asynchronous function, surfacing the result
        through an observable sequence.

        Keyword arguments:
        function_async -- Asynchronous function which returns a Future
            to run.

        Returns an observable sequence exposing the function's result
        value, or an exception.
        """
        from ..operators.startasync import start_async
        return start_async(function_async)

    @staticmethod
    def throw(exception: Exception) -> Observable:
        """Returns an observable sequence that terminates with an
        exception, using the specified scheduler to send out the single
        OnError message.

        1 - res = rx.Observable.throw(Exception('Error'))

        Keyword arguments:
        exception -- An object used for the sequence's termination.

        Returns the observable sequence that terminates exceptionally
        with the specified exception object.
        """
        from ..operators.throw import throw
        return throw(exception)

    @staticmethod
    def on_error_resume_next(*args) -> Observable:
        """Continues an observable sequence that is terminated normally or by
        an exception with the next observable sequence.

        1 - res = Observable.on_error_resume_next(xs, ys, zs)
        2 - res = Observable.on_error_resume_next([xs, ys, zs])

        Returns an observable sequence that concatenates the source sequences,
        even if a sequence terminates exceptionally.
        """
        from ..operators.onerrorresumenext import on_error_resume_next
        return on_error_resume_next(*args)

    on_error_resume_next = on_error_resume_next

    @staticmethod
    def timer(duetime: Union[datetime, int], period=None) -> Observable:
        """Returns an observable sequence that produces a value after
        duetime has elapsed and then after each period.

        1 - res = Observable.timer(datetime(...))
        2 - res = Observable.timer(datetime(...), 1000)

        5 - res = Observable.timer(5000)
        6 - res = Observable.timer(5000, 1000)

        Keyword arguments:
        duetime -- Absolute (specified as a Date object) or relative
            time (specified as an integer denoting milliseconds) at
            which to produce the first value.
        period -- [Optional] Period to produce subsequent values
            (specified as an integer denoting milliseconds). If not
            specified, the resulting timer is not recurring.

        Returns an observable sequence that produces a value after due
        time has elapsed and then each period.
        """
        from ..operators.timer import timer
        return timer(duetime, period)

    @staticmethod
    def to_async(func: Callable, scheduler=None) -> Callable:
        """Converts the function into an asynchronous function. Each
        invocation of the resulting asynchronous function causes an
        invocation of the original synchronous function on the specified
        scheduler.

        Example:
        res = Observable.to_async(lambda x, y: x + y)(4, 3)
        res = Observable.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        res = Observable.to_async(lambda x: log.debug(x),
                                Scheduler.timeout)('hello')

        func -- Function to convert to an asynchronous function.
        scheduler -- [Optional] Scheduler to run the function on. If not
            specified, defaults to Scheduler.timeout.

        Returns asynchronous function.
        """
        from ..operators.toasync import to_async
        return to_async(func, scheduler)

    @staticmethod
    def using(resource_factory, observable_factory) -> Observable:
        """Constructs an observable sequence that depends on a resource
        object, whose lifetime is tied to the resulting observable
        sequence's lifetime.

        1 - res = rx.Observable.using(lambda: AsyncSubject(), lambda: s: s)

        Keyword arguments:
        resource_factory -- Factory function to obtain a resource
            object.
        observable_factory -- Factory function to obtain an observable
            sequence that depends on the obtained resource.

        Returns an observable sequence whose lifetime controls the
        lifetime of the dependent resource object.
        """
        from ..operators.using import using
        return using(resource_factory, observable_factory)

    @staticmethod
    def when(*args) -> Observable:
        """Joins together the results from several patterns.

        args -- A series of plans (specified as a list of as a series of
            arguments) created by use of the Then operator on patterns.

        Returns Observable sequence with the results form matching
        several patterns.
        """
        from ..operators.when import when
        return when(*args)

    @staticmethod
    def while_do(condition: Callable[[Any], bool], source: Observable) -> Observable:
        """Repeats source as long as condition holds emulating a while
        loop.

        Keyword arguments:
        condition -- The condition which determines if the source will
            be repeated.

        Returns an observable sequence which is repeated as long as the
            condition holds.
        """
        from ..operators.whiledo import while_do
        return while_do(condition, source)

    @staticmethod
    def zip(*args: Union[Iterable[Observable], Observable],
            result_mapper: Mapper = None) -> Observable:
        """Merges the specified observable sequences into one observable
        sequence by using the mapper function whenever all of the
        observable sequences or an array have produced an element at a
        corresponding index.

        The last element in the arguments must be a function to invoke
        for each series of elements at corresponding indexes in the
        sources.

        1 - res = Observable.zip(obs2, result_mapper=fn)
        2 - res = Observable.zip([1,2,3], result_mapper=fn)

        Keyword arguments:
        args -- Observable sources to zip.
        result_mapper -- Selector function that produces an element
            whenever all of the observable sequences have produced an
            element at a corresponding index

        Returns an observable sequence containing the result of
        combining elements of the sources using the specified result
        mapper function.
        """
        from ..operators.zip import zip as _zip
        return _zip(*args, result_mapper=result_mapper)
