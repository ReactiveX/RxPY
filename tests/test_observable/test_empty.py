import unittest

from rx.core import Observable
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


class TestEmpty(unittest.TestCase):
    def test_empty_basic(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.empty(scheduler)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_completed(201))

    def test_empty_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.empty(scheduler)

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_empty_observer_throw_exception(self):
        scheduler = TestScheduler()
        xs = Observable.empty(scheduler)
        xs.subscribe(lambda x: None, lambda ex: None, lambda: _raise('ex'))

        with self.assertRaises(RxException):
            scheduler.start()

