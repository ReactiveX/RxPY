# pylint: disable=too-many-lines,redefined-outer-name,redefined-builtin

from asyncio.futures import Future as _Future
from typing import Iterable, Callable, Any, Optional, Union, Mapping

from .core import Observable, pipe, typing
from .internal.utils import alias


# Please make sure the version here remains the same as in project.cfg
__version__ = '3.1.1'


def amb(*sources: Observable) -> Observable:
    """Propagates the observable sequence that emits first.

    .. marble::
        :alt: amb

        ---8--6--9-----------|
        --1--2--3---5--------|
        ----------10-20-30---|
        [        amb()       ]
        --1--2--3---5--------|

    Example:
        >>> winner = rx.amb(xs, ys, zs)

    Args:
        sources: Sequence of observables to monitor for first emission.

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever emitted the first element.
    """

    from .core.observable.amb import _amb
    return _amb(*sources)


def case(mapper: Callable[[], Any],
         sources: Mapping,
         default_source: Optional[Union[Observable, _Future]] = None
         ) -> Observable:
    """Uses mapper to determine which source in sources to use.

    .. marble::
        :alt: case

        --1---------------|
        a--1--2--3--4--|
         b--10-20-30---|
        [case(mapper, { 1: a, 2: b })]
        ---1--2--3--4--|

    Examples:
        >>> res = rx.case(mapper, { '1': obs1, '2': obs2 })
        >>> res = rx.case(mapper, { '1': obs1, '2': obs2 }, obs0)

    Args:
        mapper: The function which extracts the value for to test in a
            case statement.
        sources: An object which has keys which correspond to the case
            statement labels.
        default_source: [Optional] The observable sequence or Future that will
            be run if the sources are not matched. If this is not provided,
            it defaults to :func:`empty`.

    Returns:
        An observable sequence which is determined by a case statement.
    """

    from .core.observable.case import _case
    return _case(mapper, sources, default_source)


def catch(*sources: Observable) -> Observable:
    """Continues observable sequences which are terminated with an
    exception by switching over to the next observable sequence.

    .. marble::
        :alt: catch

        ---1---2---3-*
                     a-7-8-|
        [      catch(a)    ]
        ---1---2---3---7-8-|

    Examples:
        >>> res = rx.catch(xs, ys, zs)

    Args:
        sources: Sequence of observables.

    Returns:
        An observable sequence containing elements from consecutive observables
        from the sequence of sources until one of them terminates successfully.
    """

    from .core.observable.catch import _catch_with_iterable
    return _catch_with_iterable(sources)


def catch_with_iterable(sources: Iterable[Observable]) -> Observable:
    """Continues observable sequences that are terminated with an
    exception by switching over to the next observable sequence.

    .. marble::
        :alt: catch

        ---1---2---3-*
                     a-7-8-|
        [      catch(a)    ]
        ---1---2---3---7-8-|

    Examples:
        >>> res = rx.catch([xs, ys, zs])
        >>> res = rx.catch(src for src in [xs, ys, zs])

    Args:
        sources: An Iterable of observables; thus, a generator can also
            be used here.

    Returns:
        An observable sequence containing elements from consecutive observables
        from the sequence of sources until one of them terminates successfully.
    """

    from .core.observable.catch import _catch_with_iterable
    return _catch_with_iterable(sources)


def create(subscribe: typing.Subscription) -> Observable:
    """Creates an observable sequence object from the specified
        subscription function.

    .. marble::
        :alt: create

        [     create(a)    ]
        ---1---2---3---4---|

    Args:
        subscribe: Subscription function.

    Returns:
        An observable sequence that can be subscribed to via the given
        subscription function.
    """

    return Observable(subscribe)


def combine_latest(*sources: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the observable
    sequences emits an element.

    .. marble::
        :alt: combine_latest

        ---a-----b--c------|
        --1---2--------3---|
        [ combine_latest() ]
        ---a1-a2-b2-c2-c3--|

    Examples:
        >>> obs = rx.combine_latest(obs1, obs2, obs3)

    Args:
        sources: Sequence of observables.

    Returns:
        An observable sequence containing the result of combining elements from
        each source in given sequence.
    """

    from .core.observable.combinelatest import _combine_latest
    return _combine_latest(*sources)


def concat(*sources: Observable) -> Observable:
    """Concatenates all of the specified observable sequences.

    .. marble::
        :alt: concat

        ---1--2--3--|
        --6--8--|
        [     concat()     ]
        ---1--2--3----6--8-|

    Examples:
        >>> res = rx.concat(xs, ys, zs)

    Args:
        sources: Sequence of observables.

    Returns:
        An observable sequence that contains the elements of each source in
        the given sequence, in sequential order.
    """

    from .core.observable.concat import _concat_with_iterable
    return _concat_with_iterable(sources)


def concat_with_iterable(sources: Iterable[Observable]) -> Observable:
    """Concatenates all of the specified observable sequences.

    .. marble::
        :alt: concat

        ---1--2--3--|
        --6--8--|
        [     concat()     ]
        ---1--2--3----6--8-|

    Examples:
        >>> res = rx.concat_with_iterable([xs, ys, zs])
        >>> res = rx.concat_with_iterable(for src in [xs, ys, zs])

    Args:
        sources: An Iterable of observables; thus, a generator can also
            be used here.

    Returns:
        An observable sequence that contains the elements of each given
        sequence, in sequential order.
    """

    from .core.observable.concat import _concat_with_iterable
    return _concat_with_iterable(sources)


def defer(factory: Callable[[typing.Scheduler], Union[Observable, _Future]]
          ) -> Observable:
    """Returns an observable sequence that invokes the specified
    factory function whenever a new observer subscribes.

    .. marble::
        :alt: defer

        [     defer(1,2,3)     ]
        ---1--2--3--|
                ---1--2--3--|

    Example:
        >>> res = rx.defer(lambda: of(1, 2, 3))

    Args:
        factory: Observable factory function to invoke for each observer
            which invokes :func:`subscribe() <rx.Observable.subscribe>` on
            the resulting sequence.

    Returns:
        An observable sequence whose observers trigger an invocation
        of the given factory function.
    """

    from .core.observable.defer import _defer
    return _defer(factory)


def empty(scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an empty observable sequence.

    .. marble::
        :alt: empty

        [     empty()     ]
        --|

    Example:
        >>> obs = rx.empty()

    Args:
        scheduler: [Optional] Scheduler instance to send the termination call
            on. By default, this will use an instance of
            :class:`ImmediateScheduler <rx.scheduler.ImmediateScheduler>`.

    Returns:
        An observable sequence with no elements.
    """

    from .core.observable.empty import _empty
    return _empty(scheduler)


def for_in(values: Iterable[Any], mapper: typing.Mapper) -> Observable:
    """Concatenates the observable sequences obtained by running the
    specified result mapper for each element in the specified values.

    .. marble::
        :alt: for_in

        a--1--2-|
         b--10--20-|
        [for_in((a, b), lambda i: i+1)]
        ---2--3--11--21-|


    Note:
        This is just a wrapper for
        :func:`rx.concat(map(mapper, values)) <rx.concat>`

    Args:
        values: An Iterable of values to turn into an observable
            source.
        mapper: A function to apply to each item in the values list to turn
            it into an observable sequence; this should return instances of
            :class:`rx.Observable`.

    Returns:
        An observable sequence from the concatenated observable
        sequences.
    """

    return concat_with_iterable(map(mapper, values))


def from_callable(supplier: Callable[[], Any],
                  scheduler: Optional[typing.Scheduler] = None
                  ) -> Observable:
    """Returns an observable sequence that contains a single element generated
    by the given supplier, using the specified scheduler to send out observer
    messages.

    .. marble::
        :alt: from_callable

        [ from_callable() ]
        --1--|

    Examples:
        >>> res = rx.from_callable(lambda: calculate_value())
        >>> res = rx.from_callable(lambda: 1 / 0) # emits an error

    Args:
        supplier: Function which is invoked to obtain the single element.
        scheduler: [Optional] Scheduler instance to schedule the values on.
            If not specified, the default is to use an instance of
            :class:`CurrentThreadScheduler <rx.scheduler.CurrentThreadScheduler>`.

    Returns:
        An observable sequence containing the single element obtained by
        invoking the given supplier function.
    """

    from .core.observable.returnvalue import _from_callable
    return _from_callable(supplier, scheduler)


def from_callback(func: Callable,
                  mapper: Optional[typing.Mapper] = None
                  ) -> Callable[[], Observable]:
    """Converts a callback function to an observable sequence.

    Args:
        func: Function with a callback as the last argument to
            convert to an Observable sequence.
        mapper: [Optional] A mapper which takes the arguments
            from the callback to produce a single item to yield on
            next.

    Returns:
        A function, when executed with the required arguments minus
        the callback, produces an Observable sequence with a single
        value of the arguments to the callback as a list.
    """
    from .core.observable.fromcallback import _from_callback
    return _from_callback(func, mapper)


def from_future(future: _Future) -> Observable:
    """Converts a Future to an Observable sequence

    .. marble::
        :alt: from_future

        [  from_future()  ]
        ------1|

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


def from_iterable(iterable: Iterable, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Converts an iterable to an observable sequence.

    .. marble::
        :alt: from_iterable

        [   from_iterable(1,2,3)    ]
        ---1--2--3--|


    Example:
        >>> rx.from_iterable([1,2,3])

    Args:
        iterable: An Iterable to change into an observable sequence.
        scheduler: [Optional] Scheduler instance to schedule the values on.
            If not specified, the default is to use an instance of
            :class:`CurrentThreadScheduler <rx.scheduler.CurrentThreadScheduler>`.

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """
    from .core.observable.fromiterable import from_iterable as from_iterable_
    return from_iterable_(iterable, scheduler)


from_ = alias('from_', 'Alias for :func:`rx.from_iterable`.', from_iterable)
from_list = alias('from_list', 'Alias for :func:`rx.from_iterable`.', from_iterable)


def from_marbles(string: str,
                 timespan: typing.RelativeTime = 0.1,
                 scheduler: Optional[typing.Scheduler] = None,
                 lookup: Optional[Mapping] = None,
                 error: Optional[Exception] = None
                 ) -> Observable:
    """Convert a marble diagram string to a cold observable sequence, using
    an optional scheduler to enumerate the events.

    .. marble::
        :alt: from_marbles

        [  from_marbles(-1-2-3-)   ]
        -1-2-3-|

    Each character in the string will advance time by timespan
    (except for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. Numbers will be cast
    to int or float.

    Special characters:
        +------------+--------------------------------------------------------+
        | :code:`-`  | advance time by timespan                               |
        +------------+--------------------------------------------------------+
        | :code:`#`  | on_error()                                             |
        +------------+--------------------------------------------------------+
        | :code:`|`  | on_completed()                                         |
        +------------+--------------------------------------------------------+
        | :code:`(`  | open a group of marbles sharing the same timestamp     |
        +------------+--------------------------------------------------------+
        | :code:`)`  | close a group of marbles                               |
        +------------+--------------------------------------------------------+
        | :code:`,`  | separate elements in a group                           |
        +------------+--------------------------------------------------------+
        | <space>    | used to align multiple diagrams, does not advance time |
        +------------+--------------------------------------------------------+

    In a group of elements, the position of the initial :code:`(` determines the
    timestamp at which grouped elements will be emitted.
    E.g. :code:`--(12,3,4)--` will emit 12, 3, 4 at 2 * timespan and then
    advance virtual time by 8 * timespan.

    Examples:
        >>> from_marbles('--1--(2,3)-4--|')
        >>> from_marbles('a--b--c-', lookup={'a': 1, 'b': 2, 'c': 3})
        >>> from_marbles('a--b---#', error=ValueError('foo'))

    Args:
        string: String with marble diagram
        timespan: [Optional] Duration of each character in seconds.
            If not specified, defaults to :code:`0.1`.
        scheduler: [Optional] Scheduler to run the the input sequence
            on. If not specified, defaults to the subscribe scheduler
            if defined, else to an instance of
            :class:`NewThreadScheduler <rx.scheduler.NewThreadScheduler`.
        lookup: [Optional] A dict used to convert an element into a specified
            value. If not specified, defaults to :code:`{}`.
        error: [Optional] Exception that will be use in place of the :code:`#`
            symbol. If not specified, defaults to :code:`Exception('error')`.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    from .core.observable.marbles import from_marbles as _from_marbles
    return _from_marbles(string, timespan, lookup=lookup, error=error, scheduler=scheduler)


cold = alias('cold', 'Alias for :func:`rx.from_marbles`.', from_marbles)


def generate_with_relative_time(initial_state: Any,
                                condition: typing.Predicate,
                                iterate: typing.Mapper,
                                time_mapper: Callable[[Any], typing.RelativeTime]
                                ) -> Observable:
    """Generates an observable sequence by iterating a state from an
    initial state until the condition fails.

    .. marble::
        :alt: generate_with_relative_time

        [generate_with_relative_time()]
        -1-2-3-4-|

    Example:
        >>> res = rx.generate_with_relative_time(0, lambda x: True, lambda x: x + 1, lambda x: 0.5)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            :code:`False`).
        iterate: Iteration step function.
        time_mapper: Time mapper function to control the speed of
            values being produced each iteration, returning relative times, i.e.
            either a :class:`float` denoting seconds, or an instance of
            :class:`timedelta`.

    Returns:
        The generated sequence.
    """
    from .core.observable.generatewithrelativetime import _generate_with_relative_time
    return _generate_with_relative_time(initial_state, condition, iterate, time_mapper)


def generate(initial_state: Any,
             condition: typing.Predicate,
             iterate: typing.Mapper
             ) -> Observable:
    """Generates an observable sequence by running a state-driven loop
    producing the sequence's elements.

    .. marble::
        :alt: generate

        [   generate()    ]
        -1-2-3-4-|

    Example:
        >>> res = rx.generate(0, lambda x: x < 10, lambda x: x + 1)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            :code:`False`).
        iterate: Iteration step function.

    Returns:
        The generated sequence.
    """
    from .core.observable.generate import _generate
    return _generate(initial_state, condition, iterate)


def hot(string: str,
        timespan: typing.RelativeTime=0.1,
        duetime:typing.AbsoluteOrRelativeTime = 0.0,
        scheduler: Optional[typing.Scheduler] = None,
        lookup: Optional[Mapping] = None,
        error: Optional[Exception] = None
        ) -> Observable:
    """Convert a marble diagram string to a hot observable sequence, using
    an optional scheduler to enumerate the events.

    .. marble::
        :alt: hot

        [  from_marbles(-1-2-3-)   ]
        -1-2-3-|
          -2-3-|

    Each character in the string will advance time by timespan
    (except for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. Numbers will be cast
    to int or float.

    Special characters:
        +------------+--------------------------------------------------------+
        | :code:`-`  | advance time by timespan                               |
        +------------+--------------------------------------------------------+
        | :code:`#`  | on_error()                                             |
        +------------+--------------------------------------------------------+
        | :code:`|`  | on_completed()                                         |
        +------------+--------------------------------------------------------+
        | :code:`(`  | open a group of elements sharing the same timestamp    |
        +------------+--------------------------------------------------------+
        | :code:`)`  | close a group of elements                              |
        +------------+--------------------------------------------------------+
        | :code:`,`  | separate elements in a group                           |
        +------------+--------------------------------------------------------+
        | <space>    | used to align multiple diagrams, does not advance time |
        +------------+--------------------------------------------------------+

    In a group of elements, the position of the initial :code:`(` determines the
    timestamp at which grouped elements will be emitted.
    E.g. :code:`--(12,3,4)--` will emit 12, 3, 4 at 2 * timespan and then
    advance virtual time by 8 * timespan.

    Examples:
        >>> hot("--1--(2,3)-4--|")
        >>> hot("a--b--c-", lookup={'a': 1, 'b': 2, 'c': 3})
        >>> hot("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram
        timespan: [Optional] Duration of each character in seconds.
            If not specified, defaults to :code:`0.1`.
        duetime: [Optional] Absolute datetime or timedelta from now that
            determines when to start the emission of elements.
        scheduler: [Optional] Scheduler to run the the input sequence
            on. If not specified, defaults to an instance of
            :class:`NewThreadScheduler <rx.scheduler.NewThreadScheduler>`.
        lookup: [Optional] A dict used to convert an element into a specified
            value. If not specified, defaults to :code:`{}`.
        error: [Optional] Exception that will be use in place of the :code:`#`
            symbol. If not specified, defaults to :code:`Exception('error')`.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    from .core.observable.marbles import hot as _hot
    return _hot(string, timespan, duetime, lookup=lookup, error=error, scheduler=scheduler)


def if_then(condition: Callable[[], bool],
            then_source: Union[Observable, _Future],
            else_source: Union[None, Observable, _Future] = None
            ) -> Observable:
    """Determines whether an observable collection contains values.

    .. marble::
        :alt: if_then

        ---1--2--3--|
        --6--8--|
        [    if_then()     ]
        ---1--2--3--|


    Examples:
        >>> res = rx.if_then(condition, obs1)
        >>> res = rx.if_then(condition, obs1, obs2)

    Args:
        condition: The condition which determines if the then_source or
            else_source will be run.
        then_source: The observable sequence or :class:`Future` that
            will be run if the condition function returns :code:`True`.
        else_source: [Optional] The observable sequence or :class:`Future`
            that will be run if the condition function returns :code:`False`.
            If this is not provided, it defaults to :func:`empty() <rx.empty>`.

    Returns:
        An observable sequence which is either the then_source or
        else_source.
    """
    from .core.observable.ifthen import _if_then
    return _if_then(condition, then_source, else_source)


def interval(period: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that produces a value after each period.

    .. marble::
        :alt: interval

        [  interval()   ]
        ---1---2---3---4--->

    Example:
        >>> res = rx.interval(1.0)

    Args:
        period: Period for producing the values in the resulting sequence
            (specified as a :class:`float` denoting seconds or an instance of
            :class:`timedelta`).
        scheduler:  Scheduler to run the interval on. If not specified, an
            instance of :class:`TimeoutScheduler <rx.scheduler.TimeoutScheduler>`
            is used.

    Returns:
        An observable sequence that produces a value after each period.
    """
    from .core.observable.interval import _interval
    return _interval(period, scheduler)


def merge(*sources: Observable) -> Observable:
    """Merges all the observable sequences into a single observable sequence.

    .. marble::
        :alt: merge

        ---1---2---3---4-|
        -a---b---c---d--|
        [     merge()      ]
        -a-1-b-2-c-3-d-4-|

    Example:
        >>> res = rx.merge(obs1, obs2, obs3)

    Args:
        sources: Sequence of observables.

    Returns:
        The observable sequence that merges the elements of the
        observable sequences.
    """
    from .core.observable.merge import _merge
    return _merge(*sources)


def never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    .. marble::
        :alt: never

        [     never()     ]
        -->

    Returns:
        An observable sequence whose observers will never get called.
    """
    from .core.observable.never import _never
    return _never()


def of(*args: Any) -> Observable:
    """This method creates a new observable sequence whose elements are taken
    from the arguments.

    .. marble::
        :alt: of

        [    of(1,2,3)    ]
        ---1--2--3--|

    Note:
        This is just a wrapper for
        :func:`rx.from_iterable(args) <rx.from_iterable>`

    Example:
        >>> res = rx.of(1,2,3)

    Args:
        args: The variable number elements to emit from the observable.

    Returns:
        The observable sequence whose elements are pulled from the
        given arguments
    """
    return from_iterable(args)


def on_error_resume_next(*sources: Union[Observable, _Future]) -> Observable:
    """Continues an observable sequence that is terminated normally or
    by an exception with the next observable sequence.

    .. marble::
        :alt: on_error_resume_next

        --1--2--*
        a--3--4--*
         b--6-|
        [on_error_resume_next(a,b)]
        --1--2----3--4----6-|

    Examples:
        >>> res = rx.on_error_resume_next(xs, ys, zs)

    Args:
        sources: Sequence of sources, each of which is expected to be an
            instance of either :class:`Observable` or :class:`Future`.

    Returns:
        An observable sequence that concatenates the source sequences,
        even if a sequence terminates with an exception.
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

    .. marble::
        :alt: range

        [    range(4)     ]
        --0--1--2--3--|

    Examples:
        >>> res = rx.range(10)
        >>> res = rx.range(0, 10)
        >>> res = rx.range(0, 10, 1)

    Args:
        start: The value of the first integer in the sequence.
        count: The number of sequential integers to generate.
        scheduler: [Optional] The scheduler to schedule the values on. If not
            specified, the default is to use an instance of
            :class:`CurrentThreadScheduler <rx.scheduler.CurrentThreadScheduler>`.

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

    .. marble::
        :alt: return_value

        [ return_value(4) ]
        -4-|

    Examples:
        >>> res = rx.return_value(42)
        >>> res = rx.return_value(42, timeout_scheduler)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified element.
    """
    from .core.observable.returnvalue import _return_value
    return _return_value(value, scheduler)


just = alias('just', 'Alias for :func:`rx.return_value`.', return_value)


def repeat_value(value: Any = None, repeat_count: Optional[int] = None) -> Observable:
    """Generates an observable sequence that repeats the given element
    the specified number of times.

    .. marble::
        :alt: repeat_value

        [ repeat_value(4) ]
        -4-4-4-4->

    Examples:
        >>> res = rx.repeat_value(42)
        >>> res = rx.repeat_value(42, 4)

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


def start(func: Callable, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Invokes the specified function asynchronously on the specified
    scheduler, surfacing the result through an observable sequence.

    .. marble::
        :alt: start

        [ start(lambda i: return 4) ]
        -4-|
          -4-|

    Note:
        The function is called immediately, not during the subscription
        of the resulting sequence. Multiple subscriptions to the
        resulting sequence can observe the function's result.

    Example:
        >>> res = rx.start(lambda: pprint('hello'))
        >>> res = rx.start(lambda: pprint('hello'), rx.Scheduler.timeout)

    Args:
        func: Function to run asynchronously.
        scheduler: [Optional] Scheduler to run the function on. If
            not specified, defaults to an instance of
            :class:`TimeoutScheduler <rx.scheduler.TimeoutScheduler>`.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """
    from .core.observable.start import _start
    return _start(func, scheduler)


def start_async(function_async: Callable[[], _Future]) -> Observable:
    """Invokes the asynchronous function, surfacing the result through
    an observable sequence.

    .. marble::
        :alt: start_async

        [  start_async()  ]
        ------1|

    Args:
        function_async: Asynchronous function which returns a :class:`Future`
            to run.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """
    from .core.observable.startasync import _start_async
    return _start_async(function_async)


def throw(exception: Exception, scheduler: Optional[typing.Scheduler] = None) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError message.

    .. marble::
        :alt: throw

        [ throw() ]
        -*

    Example:
        >>> res = rx.throw(Exception('Error'))

    Args:
        exception: An object used for the sequence's termination.
        scheduler: [Optional] Scheduler to schedule the error notification on.
            If not specified, the default is to use an instance of
            :class:`ImmediateScheduler <rx.scheduler.ImmediateScheduler>`.

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

    .. marble::
        :alt: timer

        [ timer(2) ]
        --0-|

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
            the default is to use an instance of
            :class:`TimeoutScheduler <rx.scheduler.TimeoutScheduler>`.

    Returns:
        An observable sequence that produces a value after due time has
        elapsed and then each period.
    """
    from .core.observable.timer import _timer
    return _timer(duetime, period, scheduler)


def to_async(func: Callable, scheduler: Optional[typing.Scheduler] = None) -> Callable:
    """Converts the function into an asynchronous function. Each
    invocation of the resulting asynchronous function causes an
    invocation of the original synchronous function on the specified
    scheduler.

    .. marble::
        :alt: to_async

        [  to_async()()   ]
        ------1|

    Examples:
        >>> res = rx.to_async(lambda x, y: x + y)(4, 3)
        >>> res = rx.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        >>> res = rx.to_async(lambda x: log.debug(x), Scheduler.timeout)('hello')

    Args:
        func: Function to convert to an asynchronous function.
        scheduler: [Optional] Scheduler to run the function on. If not
            specified, defaults to an instance of
            :class:`TimeoutScheduler <rx.scheduler.TimeoutScheduler>`.

    Returns:
        Asynchronous function.
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
    sequence by creating a :class:`tuple` only when the first
    observable sequence produces an element.

    .. marble::
        :alt: with_latest_from

        ---1---2---3----4-|
        --a-----b----c-d----|
        [with_latest_from() ]
        ---1,a-2,a-3,b--4,d-|

    Examples:
        >>> obs = rx.with_latest_from(obs1)
        >>> obs = rx.with_latest_from([obs1, obs2, obs3])

    Args:
        sources: Sequence of observables.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a :class:`tuple`.
    """
    from .core.observable.withlatestfrom import _with_latest_from
    return _with_latest_from(*sources)


def zip(*args: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a :class:`tuple` whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    .. marble::
        :alt: zip

        --1--2---3-----4---|
        -a----b----c-d-----|
        [       zip()      ]
        --1,a-2,b--3,c-4,d-|

    Example:
        >>> res = rx.zip(obs1, obs2)

    Args:
        args: Observable sources to zip.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as a :class:`tuple`.
    """
    from .core.observable.zip import _zip
    return _zip(*args)
