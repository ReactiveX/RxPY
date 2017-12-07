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


class TestThrow(unittest.TestCase):
    def test_throw_exception_basic(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def factory():
            return Observable.throw_exception(ex, scheduler)

        results = scheduler.start(factory)
        results.messages.assert_equal(throw(201, ex))

    def test_throw_disposed(self):
        scheduler = TestScheduler()
        def factory():
            return Observable.throw_exception('ex', scheduler)

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_throw_observer_throws(self):
        scheduler = TestScheduler()
        xs = Observable.throw_exception('ex', scheduler)
        xs.subscribe_callbacks(lambda x: None, lambda ex: _raise('ex'), lambda: None)

        self.assertRaises(RxException, scheduler.start)

