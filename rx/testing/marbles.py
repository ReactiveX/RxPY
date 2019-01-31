from typing import List, Tuple, Union, Dict
from collections import namedtuple

import rx
from rx.core import Observable
from rx.concurrency import NewThreadScheduler
from rx.core.typing import Callable
from rx.testing import TestScheduler, Recorded, ReactiveTest
from rx.core.observable.marbles import parse

new_thread_scheduler = NewThreadScheduler()

TestContext = namedtuple('TestContext', 'start, cold, hot, exp')


def test_context(timespan=1):
    """
    Initialize a :class:`TestScheduler` and return a namedtuple containing the
    following functions that wrap its methods.

    :func:`cold()`:
    Parse a marbles string and return a cold observable

    :func:`hot()`:
    Parse a marbles string and return a hot observable

    :func:`start()`:
    Start the test scheduler and invoke the create function,
    subscribe to the resulting sequence, dispose the subscription and
    return the resulting records

    :func:`exp()`:
    Parse a marbles string and return a list of records

    Examples:
        >>> start, cold, hot, exp = test_context()

        >>> context = test_context()
        >>> context.cold("--a--b--#", error=Exception("foo"))

        >>> e0 = hot("a---^-b---c-|")
        >>> ex = exp("    --b---c-|")
        >>> results = start(e1)
        >>> assert results.messages == ex

    The underlying test scheduler is initialized with the following
    parameters:
        - created time = 100
        - subscribed = 200
        - disposed = 1000

    **IMPORTANT**: regarding :func:`hot()`, a marble declared as the
    first character will be skipped by the test scheduler.
    E.g. `hot("a--b--")` will only emit `b`.
    """

    scheduler = TestScheduler()
    created = 100
    disposed = 1000
    subscribed = 200

    def test_start(create: Union[Observable, Callable[[], Observable]]) -> List[Recorded]:

        def default_create():
            return create

        if isinstance(create, Observable):
            create_function = default_create
        else:
            create_function = create

        mock_observer = scheduler.start(
            create=create_function,
            created=created,
            subscribed=subscribed,
            disposed=disposed,
            )
        return mock_observer.messages

    def test_expected(string: str, lookup: Dict = None, error: Exception = None) -> List[Recorded]:
        if string.find('^') >= 0:
            raise ValueError(
                'Expected function does not support subscription symbol "^".'
                'Got "{}"'.format(string))

        messages = parse(
            string,
            timespan=timespan,
            time_shift=subscribed,
            lookup=lookup,
            error=error,
            )
        return messages_to_records(messages)


    def test_cold(string: str, lookup: Dict = None, error: Exception = None) -> Observable:
        if string.find('^') >= 0:
            raise ValueError(
                'Cold observable does not support subscription symbol "^".'
                'Got "{}"'.format(string))

        return rx.from_marbles(
            string,
            timespan=timespan,
            lookup=lookup,
            error=error,
            )

    def test_hot(string: str, lookup: Dict = None, error: Exception = None) -> Observable:
        hot_obs = rx.hot(
            string,
            timespan=timespan,
            start_time=subscribed,
            lookup=lookup,
            error=error,
            scheduler=scheduler,
            )
        return hot_obs

    return TestContext(test_start, test_cold, test_hot, test_expected)


def messages_to_records(messages: List[Tuple]) -> List[Recorded]:
    """
    Helper function to convert messages returned by parse() to a list of
    Recorded.
    """
    records = []

    dispatcher = dict(
        N=lambda t, n: ReactiveTest.on_next(t, n.value),
        E=lambda t, n: ReactiveTest.on_error(t, n.exception),
        C=lambda t, n: ReactiveTest.on_completed(t)
        )

    for message in messages:
        time, notification = message
        kind = notification.kind
        record = dispatcher[kind](time, notification)
        records.append(record)

    return records
