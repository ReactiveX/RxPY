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


class TestThrow(unittest.TestCase):
    def test_throw_exception_basic(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def factory():
            return Observable.throw_exception(ex, scheduler)

        results = scheduler.start(factory)
        results.messages.assert_equal(on_error(201, ex))

    def test_throw_disposed(self):
        scheduler = TestScheduler()
        def factory():
            return Observable.throw_exception('ex', scheduler)

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_throw_observer_throws(self):
        scheduler = TestScheduler()
        xs = Observable.throw_exception('ex', scheduler)
        xs.subscribe(lambda x: None, lambda ex: _raise('ex'), lambda: None)

        self.assertRaises(RxException, scheduler.start)

