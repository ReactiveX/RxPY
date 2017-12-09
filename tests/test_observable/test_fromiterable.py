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

        results.messages.assert_equal(
                            send(200, 1),
                            send(200, 2),
                            send(200, 3),
                            send(200, 4),
                            send(200, 5),
                            close(200)
                        )

    def test_subscribe_to_iterable_empty(self):
        iterable_finite = []

        scheduler = TestScheduler()

        def create():
            return Observable.from_(iterable_finite)
        results = scheduler.start(create)

        results.messages.assert_equal(close(200))

    def test_double_subscribe_to_iterable(self):
        iterable_finite = [1, 2, 3]
        scheduler = TestScheduler()
        obs = Observable.from_(iterable_finite)

        results = scheduler.start(lambda: obs.concat(obs))
        results.messages.assert_equal(send(200, 1), send(200, 2), send(200, 3), send(200, 1), send(200, 2), send(200, 3), close(200))

