import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

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
            return Observable.range(0, 0, scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(201))

    def test_range_one(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(0, 1, scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(201, 0), on_completed(202))

    def test_range_five(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(10, 5, scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(
                            on_next(201, 10),
                            on_next(202, 11),
                            on_next(203, 12),
                            on_next(204, 13),
                            on_next(205, 14),
                            on_completed(206))

    def test_range_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(-10, 5, scheduler)

        results = scheduler.start(create, disposed=204)
        results.messages.assert_equal(on_next(201, -10), on_next(202, -9), on_next(203, -8))

    def test_range_double_subscribe(self):
        scheduler = TestScheduler()
        obs = Observable.range(1, 3)

        results = scheduler.start(lambda: obs)
        results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(200, 3), on_completed(200))

        results = scheduler.start(lambda: obs)
        results.messages.assert_equal(on_next(1001, 1), on_next(1001, 2), on_next(1001, 3), on_completed(1001))
