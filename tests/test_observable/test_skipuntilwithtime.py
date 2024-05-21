import unittest
from datetime import datetime, timezone

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipUntilWithTIme(unittest.TestCase):
    def test_skipuntil_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_until_with_time(datetime.fromtimestamp(0, tz=timezone.utc)))

        res = scheduler.start(create)

        assert res.messages == [on_next(210, 1), on_next(220, 2), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skipuntil_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_until_with_time(datetime.fromtimestamp(250, tz=timezone.utc)))

        res = scheduler.start(create)

        assert res.messages == [on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skipuntil_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(210, ex))

        def create():
            return xs.pipe(ops.skip_until_with_time(datetime.fromtimestamp(250, tz=timezone.utc)))

        res = scheduler.start(create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_skipuntil_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.pipe(ops.skip_until_with_time(datetime.fromtimestamp(250, tz=timezone.utc)))

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_skipuntil_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        )

        def create():
            return xs.pipe(
                ops.skip_until_with_time(datetime.fromtimestamp(215, tz=timezone.utc)),
                ops.skip_until_with_time(datetime.fromtimestamp(230, tz=timezone.utc)),
            )

        res = scheduler.start(create)

        assert res.messages == [
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        ]
        assert xs.subscriptions == [subscribe(200, 270)]

    def test_skipuntil_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        )

        def create():
            return xs.pipe(
                ops.skip_until_with_time(datetime.fromtimestamp(230, tz=timezone.utc)),
                ops.skip_until_with_time(datetime.fromtimestamp(215, tz=timezone.utc)),
            )

        res = scheduler.start(create)

        assert res.messages == [
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        ]
        assert xs.subscriptions == [subscribe(200, 270)]
