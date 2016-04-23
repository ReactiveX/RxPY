import math
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
    def test_distinct_defaultcomparer_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 1), on_next(380, 3), on_next(400, 5), on_completed(420))

        def create():
            return xs.distinct()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(350, 1), on_next(380, 3), on_next(400, 5), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_distinct_default_comparer_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 2), on_next(380, 3), on_next(400, 4), on_completed(420))

        def create():
            return xs.distinct()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(380, 3), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_distinct_key_selector_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 8), on_next(300, 4), on_next(350, 2), on_next(380, 6), on_next(400, 10), on_completed(420))

        def create():
            def key_selector(x):
                return x / 2
            return xs.distinct(key_selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 8), on_next(300, 4), on_next(350, 2), on_next(380, 6), on_next(400, 10), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_distinct_key_selector_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 3), on_next(380, 7), on_next(400, 5), on_completed(420))

        def create():
            def key_selector(x):
                return math.floor(x / 2.0)

            return xs.distinct(key_selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(380, 7), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_distinct_key_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 3), on_next(300, 2), on_next(350, 1), on_next(380, 0), on_next(400, 4), on_completed(420))

        def create():
            def key_selector(x):
                if not x:
                    raise Exception(ex)
                else:
                    return math.floor(x / 2.0)

            return xs.distinct(key_selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(280, 3), on_next(350, 1), on_error(380, ex))
        xs.subscriptions.assert_equal(subscribe(200, 380))
