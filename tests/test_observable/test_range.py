import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestRange(unittest.TestCase):
    def test_range_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(0, 0)

        results = scheduler.start(create)
        results.messages.assert_equal(close(201))

    def test_range_one(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(0, 1)
        results = scheduler.start(create)

        results.messages.assert_equal(send(201, 0), close(202))

    def test_range_five(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(10, 5)

        results = scheduler.start(create)

        results.messages.assert_equal(
                            send(201, 10),
                            send(202, 11),
                            send(203, 12),
                            send(204, 13),
                            send(205, 14),
                            close(206))

    def test_range_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.range(-10, 5)

        results = scheduler.start(create, disposed=204)
        results.messages.assert_equal(send(201, -10), send(202, -9), send(203, -8))

    def test_range_double_subscribe(self):
        scheduler = TestScheduler()
        obs = Observable.range(1, 3)

        results = scheduler.start(lambda: obs.concat(obs))
        results.messages.assert_equal(send(202, 1), send(203, 2), send(204, 3), send(207, 1), send(208, 2), send(209, 3), close(211))

