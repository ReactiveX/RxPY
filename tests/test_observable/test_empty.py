import unittest

from rx import empty
from rx.testing import ReactiveTest, TestScheduler

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
            return empty()

        results = scheduler.start(factory)

        assert results.messages == [on_completed(200)]

    def test_empty_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return empty()

        results = scheduler.start(factory, disposed=200)
        assert results.messages == []

    def test_empty_observer_throw_exception(self):
        scheduler = TestScheduler()
        xs = empty()
        xs.subscribe(
            lambda x: None, lambda ex: None, lambda: _raise("ex"), scheduler=scheduler
        )

        with self.assertRaises(RxException):
            scheduler.start()
