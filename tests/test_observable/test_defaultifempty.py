import unittest

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


class TestDistinctUntilChanged(unittest.TestCase):
    def test_default_if_empty_non_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_completed(420))

        def create():
            return xs.default_if_empty()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 42), on_next(360, 43), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_default_if_empty_non_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_completed(420))

        def create():
            return xs.default_if_empty(-1)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 42), on_next(360, 43), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_default_if_empty_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(420))

        def create():
            return xs.default_if_empty(None)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(420, None), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_default_if_empty_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(420))

        def create():
            return xs.default_if_empty(-1)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(420, -1), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))
