from asyncio.futures import Future
from typing import Iterable, Callable, Any, Optional, Union

from .core import AnonymousObservable, Observer, Observable, abc, typing

def amb(*args: Observable):
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever reacted first.
    """
    from .core.observable.amb import _amb
    return _amb(*args)


def case(mapper, sources, default_source=None) -> Observable:
    """Uses mapper to determine which source in sources to use.

    Examples:
        >>> res = case(mapper, { '1': obs1, '2': obs2 })
        >>> res = case(mapper, { '1': obs1, '2': obs2 }, obs0)

    Args:
        mapper -- The function which extracts the value for to test in a
            case statement.
        sources -- An object which has keys which correspond to the case
            statement labels.
        default_source -- The observable sequence or Future that will be run
            if the sources are not matched. If this is not provided, it
            defaults to rx.Observabe.empty.

    Returns:
        An observable sequence which is determined by a case statement.
    """
    from .core.observable.case import _case
    return _case(mapper, sources, default_source)

def catch_exception(*args: Observable) -> Observable:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> res = catch_exception(xs, ys, zs)
        >>> res = catch_exception([xs, ys, zs])

    Returns:
        An observable sequence containing elements from consecutive
        source sequences until a source sequence terminates
        successfully.
    """
    from .core.observable.catch import _catch_exception
    return _catch_exception(*args)

def create(subscribe: Callable[[typing.Observer, Optional[typing.Scheduler]], typing.Disposable]):
    """Create observable from subscribe function."""

    return AnonymousObservable(subscribe)

def concat(*args: Union[Observable, Iterable[Observable]]) -> Observable:
    """Concatenates all the observable sequences.

    Examples:
        >>> res = concat(xs, ys, zs)
        >>>res = concat([xs, ys, zs])

    Returns:
        An observable sequence that contains the elements of each given
        sequence, in sequential order.
    """
    from .core.observable.concat import _concat
    return _concat(*args)

def defer(observable_factory: Callable[[abc.Scheduler], Observable]) -> Observable:
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
        >>> res = defer(lambda: of(1, 2, 3))

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
        >>> obs = empty()

    Args:
        scheduler: Scheduler to send the termination call on.

    Returns:
        An observable sequence with no elements.
    """
    from .core.observable.empty import _empty
    return _empty(scheduler)

def for_in(values, result_mapper) -> Observable:
    """Concatenates the observable sequences obtained by running the
    specified result mapper for each element in source.

    Args:
        values: A list of values to turn into an observable sequence.
        result_mapper: A function to apply to each item in the values
            list to turn it into an observable sequence.
    Returns:
        An observable sequence from the concatenated observable
        sequences.
    """
    from .core.observable.empty import _for_in
    return _for_in(values, result_mapper)

def from_callable(supplier: Callable, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element
    generate from a supplier, using the specified scheduler to send out
    observer messages.

    Examples:
        >>> res = from_callable(lambda: calculate_value())
        >>> res = from_callable(lambda: 1 / 0) # emits an error

    Args:
        value: Single element in the resulting observable sequence.
        scheduler: Scheduler to schedule the values on.

    Returns:
        An observable sequence containing the single specified
        element derived from the supplier
    """
    from .core.observable.returnvalue import _from_callable
    return _from_callable(supplier, scheduler)


def from_future(future: Future) -> Observable:
    """Converts a Future to an Observable sequence

    Args:
        future: A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

    Returns:
        An observable sequence which wraps the existing future success
        and failure.
    """
    from .core.observable.fromfuture import from_future as from_future_
    return from_future_(future)


def from_iterable(iterable: Iterable) -> Observable:
    """Converts an iterable to an observable sequence.

    Example:
        >>> from_iterable([1,2,3])

    Args:
        iterable - A Python iterable
        scheduler: An optional scheduler to schedule the values on.

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """
    from .core.observable.fromiterable import from_iterable as from_iterable_
    return from_iterable_(iterable)


from_ = from_iterable
from_list = from_iterable


def from_range(start: int, stop: int = None, step: int = None, scheduler: typing.Scheduler = None) -> Observable:
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    Examples:
        >>> res = range(10)
        >>> res = range(0, 10)
        >>> res = range(0, 10, 1)

    Args:
        start: The value of the first integer in the sequence.
        count: The number of sequential integers to generate.
        scheduler: The scheduler to schedule the values on.

    Returns:
        An observable sequence that contains a range of sequential
        integral numbers.
    """
    from .core.observable.range import from_range as from_range_
    return from_range_(start, stop, step)

def generate(initial_state, condition, iterate, result_mapper) -> Observable:
    """Generates an observable sequence by running a state-driven loop
    producing the sequence's elements, using the specified scheduler to
    send out observer messages.

    Example:
        >>> res = generate(0, lambda x: x < 10, lambda x: x + 1,
                           lambda x: x)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            False).
        iterate: Iteration step function.
        result_mapper: Selector function for results produced in the
            sequence.

    Returns:
        The generated sequence.
    """
    from .core.observable.generate import _generate
    return _generate(initial_state, condition, iterate, result_mapper)


def interval(period, scheduler: typing.Scheduler) -> Observable:
    """Returns an observable sequence that produces a value after each
    period.

    Example:
        >>> res = interval(1000)

    Args:
        period: Period for producing the values in the resulting
            sequence (specified as an integer denoting milliseconds).
        scheduler:  Scheduler to run the interval on. If not specified,
            the timeout scheduler is used.

    Returns:
        An observable sequence that produces a value after each period.
    """
    from .core.observable.interval import _interval
    return _interval(period, scheduler)


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
    res = of(1,2,3)

    Returns:
        The observable sequence whose elements are pulled from the
        given arguments
    """
    return from_iterable(args)


def return_value(value: Any, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    Examples:
        >>> res = return_value(42)
        >>> res = return_value(42, timeout_scheduler)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified
        element.
    """
    from .core.observable.returnvalue import _return_value
    return _return_value(value, scheduler)


just = return_value


def throw(exception: Exception, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError
    message.

    Example:
        >>> res = throw(Exception('Error'))

    Args:
        exception: An object used for the sequence's termination.
        scheduler: Scheduler to schedule the error notification on.

    Returns:
        The observable sequence that terminates exceptionally with the
        specified exception object.
    """
    from .core.observable.throw import _throw
    return _throw(exception, scheduler)


def timer(duetime, period=None, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that produces a value after duetime
    has elapsed and then after each period.

    Examples:
        >>> res = Observable.timer(datetime(...))
        >>> res = Observable.timer(datetime(...), 1000)
        >>> res = Observable.timer(5000)
        >>> res = Observable.timer(5000, 1000)

    Args:
        duetime: Absolute (specified as a datetime object) or relative
            time (specified as an integer denoting milliseconds) at
            which to produce the first value.
        period: [Optional] Period to produce subsequent values
            (specified as an integer denoting milliseconds), or the
            scheduler to run the timer on. If not specified, the
            resulting timer is not recurring.
        scheduler:  Scheduler to run the timer on. If not specified,
            the timeout scheduler is used.

    Returns:
        An observable sequence that produces a value after due time has
        elapsed and then each period.
    """
    from .core.observable.timer import _timer
    return _timer(duetime, period, scheduler)
