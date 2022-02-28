import unittest

import reactivex
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
def _raise(ex):
    raise RxException(ex)


class TestFromIterable(unittest.TestCase):
    def test_subscribe_to_iterable_finite(self):
        iterable_finite = [1, 2, 3, 4, 5]
        scheduler = TestScheduler()

        def create():
            return reactivex.from_(iterable_finite)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_next(200, 4),
            on_next(200, 5),
            on_completed(200),
        ]

    def test_subscribe_to_iterable_empty(self):
        iterable_finite = []

        scheduler = TestScheduler()

        def create():
            return reactivex.from_(iterable_finite)

        results = scheduler.start(create)

        assert results.messages == [on_completed(200)]

    def test_double_subscribe_to_iterable(self):
        iterable_finite = [1, 2, 3]
        scheduler = TestScheduler()
        obs = reactivex.from_(iterable_finite)

        results = scheduler.start(lambda: reactivex.concat(obs, obs))

        assert results.messages == [
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_completed(200),
        ]

    def test_observer_throws(self):
        with self.assertRaises(RxException):
            reactivex.from_iterable([1, 2, 3]).subscribe(lambda x: _raise("ex"))
