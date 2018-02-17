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
            return Observable.from_(iterable_finite)

        results = scheduler.start(create)

        assert results.messages == [
                            on_next(200, 1),
                            on_next(200, 2),
                            on_next(200, 3),
                            on_next(200, 4),
                            on_next(200, 5),
                            on_completed(200)]

    def test_subscribe_to_iterable_empty(self):
        iterable_finite = []

        scheduler = TestScheduler()

        def create():
            return Observable.from_(iterable_finite)
        results = scheduler.start(create)

        assert results.messages == [on_completed(200)]

    def test_double_subscribe_to_iterable(self):
        iterable_finite = [1, 2, 3]
        scheduler = TestScheduler()
        obs = Observable.from_(iterable_finite)

        results = scheduler.start(lambda: obs.concat(obs))
        assert results.messages == [on_next(200, 1), on_next(200, 2), on_next(200, 3), on_next(200, 1), on_next(200, 2), on_next(200, 3), on_completed(200)]

