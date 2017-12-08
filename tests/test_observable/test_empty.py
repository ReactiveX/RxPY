import unittest

from rx.core import Observable
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


class TestEmpty(unittest.TestCase):
    def test_empty_basic(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.empty()
        results = scheduler.start(factory)

        results.messages.assert_equal(close(201))

    def test_empty_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.empty()

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_empty_observer_throw_exception(self):
        scheduler = TestScheduler()
        xs = Observable.empty()
        xs.subscribe_callbacks(lambda x: None, lambda ex: None, lambda: _raise('ex'), scheduler)

        with self.assertRaises(RxException):
            scheduler.start()

