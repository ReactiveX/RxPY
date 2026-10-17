import unittest
from typing import NoReturn

import pytest

import reactivex
from reactivex import operators as ops
from reactivex.scheduler import ImmediateScheduler
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex: Exception) -> NoReturn:
    raise RxException(ex)


class TestTimeoutWithSelector(unittest.TestCase):
    def test_timeout_duration_simple_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: ys))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_completed(450),
        ]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert ys.subscriptions == [
            subscribe(200, 310),
            subscribe(310, 350),
            subscribe(350, 420),
            subscribe(420, 450),
        ]

    def test_timeout_duration_simple_timeoutfirst(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable(on_next(100, "boo!"))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        self.assertEqual(1, len(results.messages))
        assert results.messages[0].time == 300 and results.messages[0].value.exception
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(200, 300)]
        assert zs.subscriptions == []

    def test_timeout_duration_simple_timeout_later(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_next(50, "boo!"))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert on_next(310, 1).equals(results.messages[0])
        assert on_next(350, 2).equals(results.messages[1])
        assert results.messages[2].time == 400 and results.messages[2].value.exception
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_timeout_by_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_completed(50))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert on_next(310, 1).equals(results.messages[0])
        assert on_next(350, 2).equals(results.messages[1])
        assert results.messages[2].time == 400 and results.messages[2].value.exception
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_timeout_by_completion2(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            def mapper(x):
                if x < 3:
                    return zs
                else:
                    raise Exception(ex)

            return xs.pipe(ops.timeout_with_mapper(ys, mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_error(420, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 420)]

    def test_timeout_duration_simple_inner_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_error(50, ex))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        assert results.messages == [on_next(310, 1), on_next(350, 2), on_error(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_first_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450)
        )
        ys = scheduler.create_cold_observable(on_error(50, ex))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        assert results.messages == [on_error(250, ex)]
        assert xs.subscriptions == [subscribe(200, 250)]
        assert ys.subscriptions == [subscribe(200, 250)]
        assert zs.subscriptions == []

    def test_timeout_duration_simple_source_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex)
        )
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_error(450, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [
            subscribe(310, 350),
            subscribe(350, 420),
            subscribe(420, 450),
        ]


@pytest.mark.parametrize("timeout_completes", [False, True])
@pytest.mark.parametrize("first_timeout", [False, True])
def test_timeout_fallback_preserves_scheduler(
    timeout_completes: bool, first_timeout: bool
) -> None:
    scheduler = TestScheduler()
    source = scheduler.create_hot_observable(
        on_next(210, 1), on_next(300, 2), on_completed(400)
    )
    timeout = scheduler.create_cold_observable(
        on_completed(5) if timeout_completes else on_next(5, 0)
    )
    fallback = reactivex.defer(
        lambda scheduler: reactivex.timer(10, scheduler=scheduler)
    )

    results = scheduler.start(
        lambda: source.pipe(
            ops.timeout_with_mapper(
                timeout if first_timeout else reactivex.never(),
                lambda _: timeout,
                fallback,
            )
        )
    )

    timeout_at = 205 if first_timeout else 215
    expected = [] if first_timeout else [on_next(210, 1)]
    expected += [on_next(timeout_at + 10, 0), on_completed(timeout_at + 10)]
    assert results.messages == expected
    assert source.subscriptions == [subscribe(200, timeout_at)]
    assert timeout.subscriptions == [
        subscribe(200 if first_timeout else 210, timeout_at)
    ]


@pytest.mark.parametrize("timeout_values", [[], [0], [0, 1]])
@pytest.mark.parametrize("first_timeout", [False, True])
def test_synchronous_timeout_keeps_fallback_active(
    timeout_values: list[int], first_timeout: bool
) -> None:
    scheduler = TestScheduler()
    source = reactivex.from_iterable([1, 2, 3], scheduler=ImmediateScheduler())
    timeout = reactivex.from_iterable(timeout_values, scheduler=ImmediateScheduler())
    fallback = scheduler.create_cold_observable(on_next(10, 42), on_completed(20))
    mapped_values: list[int] = []

    def duration(value: int) -> reactivex.Observable[int]:
        mapped_values.append(value)
        return timeout

    results = scheduler.start(
        lambda: source.pipe(
            ops.timeout_with_mapper(
                timeout if first_timeout else reactivex.never(),
                duration,
                fallback,
            )
        )
    )

    expected = [] if first_timeout else [on_next(200, 1)]
    expected += [on_next(210, 42), on_completed(220)]
    assert results.messages == expected
    assert fallback.subscriptions == [subscribe(200, 220)]
    assert mapped_values == ([] if first_timeout else [1])


@pytest.mark.parametrize("timeout_completes", [False, True])
@pytest.mark.parametrize("source_errors", [False, True])
def test_timeout_ignores_source_notifications_during_fallback_subscription(
    timeout_completes: bool, source_errors: bool
) -> None:
    scheduler = TestScheduler()
    source: Subject[int] = Subject()
    timeout = scheduler.create_cold_observable(
        on_completed(5) if timeout_completes else on_next(5, 0)
    )
    fallback = scheduler.create_cold_observable(on_next(10, 42), on_completed(20))
    source_error = RuntimeError("source error after timeout")

    def create_fallback(_scheduler):
        # The source subscription is still being replaced when this runs.
        source.on_next(99)
        if source_errors:
            source.on_error(source_error)
        else:
            source.on_completed()
        return fallback

    scheduler.schedule_absolute(210, lambda *_: source.on_next(1))
    results = scheduler.start(
        lambda: source.pipe(
            ops.timeout_with_mapper(
                reactivex.never(),
                lambda _: timeout,
                reactivex.defer(create_fallback),
            )
        )
    )

    assert results.messages == [on_next(210, 1), on_next(225, 42), on_completed(235)]
    assert timeout.subscriptions == [subscribe(210, 215)]
    assert fallback.subscriptions == [subscribe(215, 235)]
    assert not source.observers
