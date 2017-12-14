import math
import unittest

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


class TestDistinctUntilChanged(unittest.TestCase):
    def test_distinct_defaultcomparer_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 4), send(300, 2), send(350, 1), send(380, 3), send(400, 5), close(420))

        def create():
            return xs.distinct()

        results = scheduler.start(create)

        assert results.messages == [send(280, 4), send(300, 2), send(350, 1), send(380, 3), send(400, 5), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_default_comparer_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 4), send(300, 2), send(350, 2), send(380, 3), send(400, 4), close(420))

        def create():
            return xs.distinct()

        results = scheduler.start(create)

        assert results.messages == [send(280, 4), send(300, 2), send(380, 3), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_selector_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 8), send(300, 4), send(350, 2), send(380, 6), send(400, 10), close(420))

        def create():
            def key_selector(x):
                return x / 2
            return xs.distinct(key_selector)

        results = scheduler.start(create)

        assert results.messages == [send(280, 8), send(300, 4), send(350, 2), send(380, 6), send(400, 10), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_selector_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 4), send(300, 2), send(350, 3), send(380, 7), send(400, 5), close(420))

        def create():
            def key_selector(x):
                return math.floor(x / 2.0)

            return xs.distinct(key_selector)
        results = scheduler.start(create)

        assert results.messages == [send(280, 4), send(300, 2), send(380, 7), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 3), send(300, 2), send(350, 1), send(380, 0), send(400, 4), close(420))

        def create():
            def key_selector(x):
                if not x:
                    raise Exception(ex)
                else:
                    return math.floor(x / 2.0)

            return xs.distinct(key_selector)

        results = scheduler.start(create)

        assert results.messages == [send(280, 3), send(350, 1), throw(380, ex)]
        assert xs.subscriptions == [subscribe(200, 380)]
