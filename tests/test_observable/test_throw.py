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
            return Observable.throw(ex)

        results = scheduler.start(factory)
        assert results.messages == [on_error(200, ex)]

    def test_throw_disposed(self):
        scheduler = TestScheduler()
        def factory():
            return Observable.throw('ex')

        results = scheduler.start(factory, disposed=200)
        assert results.messages == []

    def test_throw_observer_throws(self):
        scheduler = TestScheduler()
        xs = Observable.throw('ex')
        xs.subscribe_(lambda x: None, lambda ex: _raise('ex'), lambda: None, scheduler=scheduler   )

        self.assertRaises(RxException, scheduler.start)

