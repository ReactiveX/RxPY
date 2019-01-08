from asyncio.futures import Future
from typing import Iterable, Callable, Any, Optional, Union

from .core import AnonymousObservable, Observer, Observable, abc, typing

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
    from .core.observable.defer import defer as defer_
    return defer_(observable_factory)


def empty(scheduler: typing.Scheduler = None) -> Observable:
    """Returns an empty observable sequence.

    Example:
        >>> obs = empty()

    Args:
        scheduler: Scheduler to send the termination call on.

    Returns:
        An observable sequence with no elements.
    """
    from .core.observable.empty import empty as empty_
    return empty_(scheduler)


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
    from .core.observable.returnvalue import from_callable as from_callable_
    return from_callable_(supplier, scheduler)


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


def never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    Returns:
        An observable sequence whose observers will never get called.
    """
    from .core.observable.never import never as never_
    return never_()


def of(*args: Any) -> Observable:
    """This method creates a new Observable instance with a variable
    number of arguments, regardless of number or type of the arguments.

    Example:
    res = of(1,2,3)

    Returns:
        The observable sequence whose elements are pulled from the given
        arguments
    """
    return from_iterable(args)


def return_value(value: Any, scheduler: typing.Scheduler = None) -> Observable:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    Examples:
        >>> res = return(42)
        >>> res = return(42, rx.Scheduler.timeout)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified
        element.
    """
    from .core.observable.returnvalue import return_value as return_value_
    return return_value_(value, scheduler)


just = return_value


def throw(exception: Exception) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError
    message.

    Example:
        >>> res = throw(Exception('Error'))

    Args:
        exception: An object used for the sequence's termination.

    Returns:
        The observable sequence that terminates exceptionally with the
        specified exception object.
    """
    from .core.observable.throw import throw as throw_
    return throw_(exception)


def timer(duetime, period=None) -> Observable:
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

    Returns:
        An observable sequence that produces a value after due time has
        elapsed and then each period.
    """
    from .core.observable.timer import timer as timer_
    return timer_(duetime, period)
