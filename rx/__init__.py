# pylint: disable=too-many-lines,redefined-outer-name,redefined-builtin

from asyncio.futures import Future as _Future
from typing import Iterable, Callable, Any, Optional, Union

from .core import Observable, abc, typing, pipe


def amb(*sources: Observable) -> Observable:
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = rx.amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given
        sequences, whichever reacted first.
    """
    from .core.observable.amb import _amb
    return _amb(*sources)


def case(mapper, sources, default_source=None) -> Observable:
    """Uses mapper to determine which source in sources to use.

    Examples:
        >>> res = rx.case(mapper, { '1': obs1, '2': obs2 })
        >>> res = rx.case(mapper, { '1': obs1, '2': obs2 }, obs0)

    Args:
        mapper: The function which extracts the value for to test in a
            case statement.
        sources: An object which has keys which correspond to the case
            statement labels.
        default_source: The observable sequence or Future that will be
            run if the sources are not matched. If this is not
            provided, it defaults to rx.Observabe.empty.

    Returns:
        An observable sequence which is determined by a case statement.
    """
    from .core.observable.case import _case
    return _case(mapper, sources, default_source)


def catch(*sources: Observable) -> Observable:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> res = rx.catch(xs, ys, zs)

    Returns:
        An observable sequence containing elements from consecutive
        source sequences until a source sequence terminates
        successfully.
    """
    from .core.observable.catch import _catch_with_iterable
    return _catch_with_iterable(sources)


def catch_with_iterable(sources: Iterable[Observable]) -> Observable:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> res = rx.catch([xs, ys, zs])
        >>> res = rx.catch(src for src in [xs, ys, zs])

    Args:
        sources: an Iterable of observables. Thus a generator is accepted.

    Returns:
        An observable sequence containing elements from consecutive
        source sequences until a source sequence terminates
        successfully.
    """
    from .core.observable.catch import _catch_with_iterable
    return _catch_with_iterable(sources)


def create(subscribe: Callable[[typing.Observer, Optional[typing.Scheduler]], typing.Disposable]):
    """Create observable from subscribe function."""

    return Observable(subscribe)


def combine_latest(*sources: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the
    observable sequences produces an element.

    Examples:
        >>> obs = rx.combine_latest(obs1, obs2, obs3)

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.
    """
    from .core.observable.combinelatest import _combine_latest
    return _combine_latest(*sources)


def concat(*sources: Observable) -> Observable:
    """Concatenates all the observable sequences.

    Examples:
        >>> res = rx.concat(xs, ys, zs)

    Returns:
        An observable sequence that contains the elements of each given
        sequence, in sequential order.
    """
    from .core.observable.concat import _concat_with_iterable
    return _concat_with_iterable(sources)


def concat_with_iterable(sources: Iterable[Observable]) -> Observable:
    """Concatenates all the observable sequences.

    Examples:
        >>> res = rx.concat_with_iterable([xs, ys, zs])
        >>> res = rx.concat_with_iterable(for src in [xs, ys, zs])

    Args:
        sources: an Iterable of observables. Thus a generator is accepted.

    Returns:
        An observable sequence that contains the elements of each given
        sequence, in sequential order.
    """
    from .core.observable.concat import _concat_with_iterable
    return _concat_with_iterable(sources)


def defer(observable_factory: Callable[[abc.Scheduler], Observable]) -> Observable:
    """Returns an observable sequence that invokes the specified
    factory function whenever a new observer subscribes.

    Example:
        >>> res = rx.defer(lambda: of(1, 2, 3))

    Args:
        observable_factory: Observable factory function to invoke for
        each observer that subscribes to the resulting sequence.

    Returns:
        An observable sequence whose observers trigger an invocation
        of the given observable factory function.
    """
    from .core.observable.defer import _defer
    return _defer(observable_factory)


def empty(scheduler: typing.Scheduler = None) -> Observable:
    """Returns an empty observable sequence.

    Example:
        >>> obs = rx.empty()

    Args:
        scheduler: Scheduler to send the termination call on.

    Returns:
        An observable sequence with no elements.
    """
    from .core.observable.empty import _empty
    return _empty(scheduler)


def for_in(values, mapper) -> Observable:
    """Concatenates the observable sequences obtained by running the
    specified result mapper for each element in source.

    Note:
        This is just a wrapper for `rx.concat(map(mapper, values))`

    Args:
        values: A list of values to turn into an observable sequence.
        mapper: A function to apply to each item in the values
            list to turn it into an observable sequence.

    Returns:
        An observable sequence from the concatenated observable
        sequences.
    """
    return concat_with_iterable(map(mapper, values))


def from_callable(supplier: Callable, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element
    generate from a supplier, using the specified scheduler to send out
    observer messages.

    Examples:
        >>> res = rx.from_callable(lambda: calculate_value())
        >>> res = rx.from_callable(lambda: 1 / 0) # emits an error

    Args:
        value: Single element in the resulting observable sequence.
        scheduler: Scheduler to schedule the values on.

    Returns:
        An observable sequence containing the single specified
        element derived from the supplier
    """
    from .core.observable.returnvalue import _from_callable
    return _from_callable(supplier, scheduler)


def from_callback(func: Callable, mapper: typing.Mapper = None) -> Callable[[], Observable]:
    """Converts a callback function to an observable sequence.

    Args:
        func: Function with a callback as the last parameter to
            convert to an Observable sequence.
        mapper: [Optional] A mapper which takes the arguments
            from the callback to produce a single item to yield on
            next.

    Returns:
        A function, when executed with the required parameters minus
        the callback, produces an Observable sequence with a single
        value of the arguments to the callback as a list.
    """
    from .core.observable.fromcallback import _from_callback
    return _from_callback(func, mapper)


def from_future(future: _Future) -> Observable:
    """Converts a Future to an Observable sequence

    Args:
        future: A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

    Returns:
        An observable sequence which wraps the existing future success
        and failure.
    """
    from .core.observable.fromfuture import _from_future
    return _from_future(future)


def from_iterable(iterable: Iterable, scheduler: typing.Scheduler = None) -> Observable:
    """Converts an iterable to an observable sequence.

    Example:
        >>> rx.from_iterable([1,2,3])

    Args:
        iterable: A Python iterable
        scheduler: An optional scheduler to schedule the values on.

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """
    from .core.observable.fromiterable import from_iterable as from_iterable_
    return from_iterable_(iterable, scheduler)


from_ = from_iterable
from_list = from_iterable


def from_marbles(string: str, timespan: typing.RelativeTime = 0.1, scheduler: typing.Scheduler = None,
                 lookup = None, error: Exception = None) -> Observable:
    """Convert a marble diagram string to a cold observable sequence, using
    an optional scheduler to enumerate the events.

    Each character in the string will advance time by timespan
    (exept for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. Numbers will be cast
    to int or float.

    Special characters:
        +--------+--------------------------------------------------------+
        |  `-`   | advance time by timespan                               |
        +--------+--------------------------------------------------------+
        |  `#`   | on_error()                                             |
        +--------+--------------------------------------------------------+
        |  `|`   | on_completed()                                         |
        +--------+--------------------------------------------------------+
        |  `(`   | open a group of marbles sharing the same timestamp     |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of marbles                               |
        +--------+--------------------------------------------------------+
        |  `,`   | separate elements in a group                           |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time |
        +--------+--------------------------------------------------------+

    In a group of elements, the position of the initial `(` determines the
    timestamp at which grouped elements will be emitted. E.g. `--(12,3,4)--`
    will emit 12, 3, 4 at 2 * timespan and then advance virtual time
    by 8 * timespan.

    Examples:
        >>> from_marbles("--1--(2,3)-4--|")
        >>> from_marbles("a--b--c-", lookup={'a': 1, 'b': 2, 'c': 3})
        >>> from_marbles("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.

        lookup: [Optional] dict used to convert an element into a specified
            value. If not specified, defaults to {}.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

        scheduler: [Optional] Scheduler to run the the input sequence
            on. If not specified, defaults to the subscribe scheduler
            if defined, else to NewThreadScheduler.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    from .core.observable.marbles import from_marbles as _from_marbles
    return _from_marbles(string, timespan, lookup=lookup, error=error, scheduler=scheduler)


cold = from_marbles


def generate_with_relative_time(initial_state, condition, iterate, time_mapper) -> Observable:
    """Generates an observable sequence by iterating a state from an
    initial state until the condition fails.

    Example:
        res = rx.generate_with_relative_time(0, lambda x: True, lambda x: x + 1, lambda x: 0.5)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            false).
        iterate: Iteration step function.
        time_mapper: Time mapper function to control the speed of
            values being produced each iteration, returning relative times, i.e.
            either floats denoting seconds or instances of timedelta.

    Returns:
        The generated sequence.
    """
    from .core.observable.generatewithrelativetime import _generate_with_relative_time
    return _generate_with_relative_time(initial_state, condition, iterate, time_mapper)


def generate(initial_state, condition, iterate) -> Observable:
    """Generates an observable sequence by running a state-driven loop
    producing the sequence's elements, using the specified scheduler to
    send out observer messages.

    Example:
        >>> res = rx.generate(0, lambda x: x < 10, lambda x: x + 1)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            False).
        iterate: Iteration step function.

    Returns:
        The generated sequence.
    """
    from .core.observable.generate import _generate
    return _generate(initial_state, condition, iterate)


def hot(string, timespan: typing.RelativeTime=0.1, duetime:typing.AbsoluteOrRelativeTime = 0.0,
        scheduler: typing.Scheduler = None, lookup=None, error: Exception = None) -> Observable:
    """Convert a marble diagram string to a hot observable sequence, using
    an optional scheduler to enumerate the events.

    Each character in the string will advance time by timespan
    (exept for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. Numbers will be cast
    to int or float.

    Special characters:
        +--------+--------------------------------------------------------+
        |  `-`   | advance time by timespan                               |
        +--------+--------------------------------------------------------+
        |  `#`   | on_error()                                             |
        +--------+--------------------------------------------------------+
        |  `|`   | on_completed()                                         |
        +--------+--------------------------------------------------------+
        |  `(`   | open a group of elemets sharing the same timestamp     |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of elements                              |
        +--------+--------------------------------------------------------+
        |  `,`   | separate elements in a group                           |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time |
        +--------+--------------------------------------------------------+

    In a group of elements, the position of the initial `(` determines the
    timestamp at which grouped elements will be emitted. E.g. `--(12,3,4)--`
    will emit 12, 3, 4 at 2 * timespan and then advance virtual time
    by 8 * timespan.

    Examples:
        >>> hot("--1--(2,3)-4--|")
        >>> hot("a--b--c-", lookup={'a': 1, 'b': 2, 'c': 3})
        >>> hot("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.

        duetime: [Optional] Absolute datetime or timedelta from now that
            determines when to start the emission of elements.

        lookup: [Optional] dict used to convert an element into a specified
            value. If not specified, defaults to {}.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

        scheduler: [Optional] Scheduler to run the the input sequence
            on. If not specified, defaults to NewThreadScheduler.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    from .core.observable.marbles import hot as _hot
    return _hot(string, timespan, duetime, lookup=lookup, error=error, scheduler=scheduler)


def if_then(condition: Callable[[], bool], then_source: Observable,
            else_source: Observable = None) -> Observable:
    """Determines whether an observable collection contains values.

    Examples:
        >>> res = rx.if_then(condition, obs1)
        >>> res = rx.if_then(condition, obs1, obs2)

    Args:
        condition: The condition which determines if the then_source or
            else_source will be run.
        then_source: The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source: [Optional] The observable sequence or
            Promise that will be run if the condition function returns
            False. If this is not provided, it defaults to
            rx.empty

    Returns:
        An observable sequence which is either the then_source or
        else_source.
    """
    from .core.observable.ifthen import _if_then
    return _if_then(condition, then_source, else_source)


def interval(period, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that produces a value after each
    period.

    Example:
        >>> res = rx.interval(1.0)

    Args:
        period: Period for producing the values in the resulting sequence
            (specified as a float denoting seconds or an instance of timedelta).
        scheduler:  Scheduler to run the interval on. If not specified,
            the timeout scheduler is used.

    Returns:
        An observable sequence that produces a value after each period.
    """
    from .core.observable.interval import _interval
    return _interval(period, scheduler)


def merge(*sources: Observable) -> Observable:
    """Merges all the observable sequences into a single observable
    sequence.

    Example:
        >>> res = rx.merge(obs1, obs2, obs3)

    Returns:
        The observable sequence that merges the elements of the
        observable sequences.
    """
    from .core.observable.merge import _merge
    return _merge(*sources)


def never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    Returns:
        An observable sequence whose observers will never get called.
    """
    from .core.observable.never import _never
    return _never()


def of(*args: Any) -> Observable:
    """This method creates a new Observable instance with a variable
    number of arguments, regardless of number or type of the arguments.

    Example:
        >>> res = rx.of(1,2,3)

    Returns:
        The observable sequence whose elements are pulled from the
        given arguments
    """
    return from_iterable(args)


def on_error_resume_next(*sources: Observable) -> Observable:
    """Continues an observable sequence that is terminated normally or
    by an exception with the next observable sequence.

    Examples:
        >>> res = rx.on_error_resume_next(xs, ys, zs)

    Returns:
        An observable sequence that concatenates the source sequences,
        even if a sequence terminates exceptionally.
    """
    from .core.observable.onerrorresumenext import _on_error_resume_next
    return _on_error_resume_next(*sources)


def range(start: int,
          stop: Optional[int] = None,
          step: Optional[int] = None,
          scheduler: Optional[typing.Scheduler] = None
          ) -> Observable:
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    Examples:
        >>> res = rx.range(10)
        >>> res = rx.range(0, 10)
        >>> res = rx.range(0, 10, 1)

    Args:
        start: The value of the first integer in the sequence.
        count: The number of sequential integers to generate.
        scheduler: The scheduler to schedule the values on.

    Returns:
        An observable sequence that contains a range of sequential
        integral numbers.
    """
    from .core.observable.range import _range
    return _range(start, stop, step, scheduler)


def return_value(value: Any, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    Examples:
        >>> res = rx.return_value(42)
        >>> res = rx.return_value(42, timeout_scheduler)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified
        element.
    """
    from .core.observable.returnvalue import _return_value
    return _return_value(value, scheduler)


just = return_value


def repeat_value(value: Any = None, repeat_count: Optional[int] = None) -> Observable:
    """Generates an observable sequence that repeats the given element
    the specified number of times.

    Examples:
        1 - res = rx.repeat_value(42)
        2 - res = rx.repeat_value(42, 4)

    Args:
        value: Element to repeat.
        repeat_count: [Optional] Number of times to repeat the element.
            If not specified, repeats indefinitely.

    Returns:
        An observable sequence that repeats the given element the
        specified number of times.
    """
    from .core.observable.repeat import _repeat_value
    return _repeat_value(value, repeat_count)


def start(func, scheduler=None) -> Observable:
    """Invokes the specified function asynchronously on the specified
    scheduler, surfacing the result through an observable sequence.

    Example:
        >>> res = rx.start(lambda: pprint('hello'))
        >>> res = rx.start(lambda: pprint('hello'), rx.Scheduler.timeout)

    Args:
        func: Function to run asynchronously.
        scheduler: [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.

    Remarks:
        The function is called immediately, not during the subscription
        of the resulting sequence. Multiple subscriptions to the
        resulting sequence can observe the function's result.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """
    from .core.observable.start import _start
    return _start(func, scheduler)


def start_async(function_async) -> Observable:
    """Invokes the asynchronous function, surfacing the result through
    an observable sequence.

    Args:
        function_async: Asynchronous function which returns a Future to
            run.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """
    from .core.observable.startasync import _start_async
    return _start_async(function_async)


def throw(exception: Exception, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError
    message.

    Example:
        >>> res = rx.throw(Exception('Error'))

    Args:
        exception: An object used for the sequence's termination.
        scheduler: Scheduler to schedule the error notification on.

    Returns:
        The observable sequence that terminates exceptionally with the
        specified exception object.
    """
    from .core.observable.throw import _throw
    return _throw(exception, scheduler)


def timer(duetime: typing.AbsoluteOrRelativeTime, period: Optional[typing.RelativeTime] = None,
          scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that produces a value after
    duetime has elapsed and then after each period.

    Examples:
        >>> res = rx.timer(datetime(...))
        >>> res = rx.timer(datetime(...), 0.1)
        >>> res = rx.timer(5.0)
        >>> res = rx.timer(5.0, 1.0)

    Args:
        duetime: Absolute (specified as a datetime object) or relative time
            (specified as a float denoting seconds or an instance of timedelta)
            at which to produce the first value.
        period: [Optional] Period to produce subsequent values (specified as a
            float denoting seconds or an instance of timedelta).
            If not specified, the resulting timer is not recurring.
        scheduler:  [Optional] Scheduler to run the timer on. If not specified,
            the timeout scheduler is used.

    Returns:
        An observable sequence that produces a value after due time has
        elapsed and then each period.
    """
    from .core.observable.timer import _timer
    return _timer(duetime, period, scheduler)


def to_async(func: Callable, scheduler=None) -> Callable:
    """Converts the function into an asynchronous function. Each
    invocation of the resulting asynchronous function causes an
    invocation of the original synchronous function on the specified
    scheduler.

    Examples:
        res = rx.to_async(lambda x, y: x + y)(4, 3)
        res = rx.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        res = rx.to_async(lambda x: log.debug(x), Scheduler.timeout)('hello')

    Args:
        func: Function to convert to an asynchronous function.
        scheduler: [Optional] Scheduler to run the function on. If not
            specified, defaults to Scheduler.timeout.

    Returns:
        Aynchronous function.
    """
    from .core.observable.toasync import _to_async
    return _to_async(func, scheduler)


def using(resource_factory: Callable[[], typing.Disposable],
          observable_factory: Callable[[typing.Disposable], Observable]
          ) -> Observable:
    """Constructs an observable sequence that depends on a resource
    object, whose lifetime is tied to the resulting observable
    sequence's lifetime.

    Example:
        >>> res = rx.using(lambda: AsyncSubject(), lambda: s: s)

    Args:
        resource_factory: Factory function to obtain a resource object.
        observable_factory: Factory function to obtain an observable
            sequence that depends on the obtained resource.

    Returns:
        An observable sequence whose lifetime controls the lifetime
        of the dependent resource object.
    """
    from .core.observable.using import _using
    return _using(resource_factory, observable_factory)


def with_latest_from(*sources: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    Examples:
        >>> obs = rx.with_latest_from(obs1)
        >>> obs = rx.with_latest_from([obs1, obs2, obs3])

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.
    """
    from .core.observable.withlatestfrom import _with_latest_from
    return _with_latest_from(*sources)


def zip(*args: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    Example:
        >>> res = rx.zip(obs1, obs2)

    Args:
        args: Observable sources to zip.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as a tuple.
    """
    from .core.observable.zip import _zip
    return _zip(*args)
