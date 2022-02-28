import unittest

import reactivex
from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipLastWithTime(unittest.TestCase):
    def test_skiplast_zero1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_last_with_time(0))

        res = scheduler.start(create)

        assert res.messages == [on_next(210, 1), on_next(220, 2), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_zero2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_last_with_time(0))

        res = scheduler.start(create)

        assert res.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_completed(230),
        ]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_some1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_last_with_time(15))

        res = scheduler.start(create)

        assert res.messages == [on_next(230, 1), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_some2(self):
        scheduler = TestScheduler()

        def create():
            return xs.pipe(ops.skip_last_with_time(45))

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_next(270, 7),
            on_next(280, 8),
            on_next(290, 9),
            on_completed(300),
        )
        res = scheduler.start(create)

        assert res.messages == [
            on_next(260, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(290, 4),
            on_next(300, 5),
            on_completed(300),
        ]
        assert xs.subscriptions == [subscribe(200, 300)]

    def test_skiplast_all(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            return xs.pipe(ops.skip_last_with_time(45))

        res = scheduler.start(create)

        assert res.messages == [on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(210, ex))

        def create():
            return xs.pipe(ops.skip_last_with_time(45))

        res = scheduler.start(create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_skiplast_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.pipe(ops.skip_last_with_time(50))

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]
