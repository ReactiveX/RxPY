from typing import List, Tuple, Union, Dict
from collections import namedtuple
from contextlib import contextmanager
from warnings import warn

import rx
from rx.core import Observable
from rx.core.notification import Notification
from rx.scheduler import NewThreadScheduler
from rx.core.typing import Callable, RelativeTime
from rx.testing import TestScheduler, Recorded, ReactiveTest
from rx.core.observable.marbles import parse

new_thread_scheduler = NewThreadScheduler()

MarblesContext = namedtuple('MarblesContext', 'start, cold, hot, exp')


@contextmanager
def marbles_testing(timespan=1.0):
    """
    Initialize a :class:`rx.testing.TestScheduler` and return a namedtuple
    containing the following functions that wrap its methods.

    :func:`cold()`:
    Parse a marbles string and return a cold observable

    :func:`hot()`:
    Parse a marbles string and return a hot observable

    :func:`start()`:
    Start the test scheduler, invoke the create function,
    subscribe to the resulting sequence, dispose the subscription and
    return the resulting records

    :func:`exp()`:
    Parse a marbles string and return a list of records

    Examples:
        >>> with marbles_testing() as (start, cold, hot, exp):
        ...     obs = hot("-a-----b---c-|")
        ...     ex = exp( "-a-----b---c-|")
        ...     results = start(obs)
        ...     assert results == ex

    The underlying test scheduler is initialized with the following
    parameters:
        - created time = 100.0s
        - subscribed = 200.0s
        - disposed = 1000.0s

    **IMPORTANT**: regarding :func:`hot()`, a marble declared as the
    first character will be skipped by the test scheduler.
    E.g. hot("a--b--") will only emit b.
    """

    scheduler = TestScheduler()
    created = 100.0
    disposed = 1000.0
    subscribed = 200.0
    start_called = False
    outside_of_context = False

    def check():
        if outside_of_context:
            warn('context functions should not be called outside of '
                 'with statement.',
                 UserWarning,
                 stacklevel=3,
                 )

        if start_called:
            warn('start() should only be called one time inside '
                 'a with statement.',
                 UserWarning,
                 stacklevel=3,
                 )

    def test_start(create: Union[Observable, Callable[[], Observable]]) -> List[Recorded]:
        nonlocal start_called
        check()

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
        start_called = True
        return mock_observer.messages

    def test_expected(string: str, lookup: Dict = None, error: Exception = None) -> List[Recorded]:
        messages = parse(
            string,
            timespan=timespan,
            time_shift=subscribed,
            lookup=lookup,
            error=error,
            )
        return messages_to_records(messages)

    def test_cold(string: str, lookup: Dict = None, error: Exception = None) -> Observable:
        check()
        return rx.from_marbles(
            string,
            timespan=timespan,
            lookup=lookup,
            error=error,
            )

    def test_hot(string: str, lookup: Dict = None, error: Exception = None) -> Observable:
        check()
        hot_obs = rx.hot(
            string,
            timespan=timespan,
            duetime=subscribed,
            lookup=lookup,
            error=error,
            scheduler=scheduler,
            )
        return hot_obs

    try:
        yield MarblesContext(test_start, test_cold, test_hot, test_expected)
    finally:
        outside_of_context = True


def messages_to_records(messages: List[Tuple[RelativeTime, Notification]]
                        ) -> List[Recorded]:
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
