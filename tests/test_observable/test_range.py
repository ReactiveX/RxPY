import unittest

import rx
from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestRange(unittest.TestCase):
    def test_range_zero(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(0, 0)

        results = scheduler.start(create)
        assert results.messages == [on_completed(200)]

    def test_range_one(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(0, 1)

        results = scheduler.start(create)

        assert results.messages == [on_next(200, 0), on_completed(200)]

    def test_range_five(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(10, 15)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(200, 10),
            on_next(200, 11),
            on_next(200, 12),
            on_next(200, 13),
            on_next(200, 14),
            on_completed(200),
        ]

    def test_range_dispose(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(-10, 5)

        results = scheduler.start(create, disposed=200)
        assert results.messages == []

    def test_range_double_subscribe(self):
        scheduler = TestScheduler()
        obs = rx.range(1, 4)

        results = scheduler.start(lambda: obs.pipe(ops.concat(obs)))
        assert results.messages == [
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_completed(200),
        ]

    def test_range_only_start(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(5)

        results = scheduler.start(create)
        assert results.messages == [
            on_next(200, 0),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_next(200, 4),
            on_completed(200),
        ]

    def test_range_step_also(self):
        scheduler = TestScheduler()

        def create():
            return rx.range(0, 10, 2)

        results = scheduler.start(create)
        assert results.messages == [
            on_next(200, 0),
            on_next(200, 2),
            on_next(200, 4),
            on_next(200, 6),
            on_next(200, 8),
            on_completed(200),
        ]
