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


class TestExpand(unittest.TestCase):

    def test_expand_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(300))

        def create():
            def selector():
                return scheduler.create_cold_observable(send(100, 1), send(200, 2), close(300))

            return xs.expand(selector)
        results = scheduler.start(create)

        results.messages.assert_equal(close(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))

    def test_expand_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_hot_observable(throw(300, ex))

        def create():
            def selector(x):
                return scheduler.create_cold_observable(send(100 + x, 2 * x), send(200 + x, 3 * x), close(300 + x))
            return xs.expand(selector)
        results = scheduler.start(create)

        results.messages.assert_equal(throw(300, ex))
        xs.subscriptions.assert_equal(subscribe(200, 300))

    def test_expand_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            def selector(x):
                return scheduler.create_cold_observable(send(100 + x, 2 * x), send(200 + x, 3 * x), close(300 + x))
            return xs.expand(selector)

        results = scheduler.start(create)

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_expand_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(550, 1), send(850, 2), close(950))

        def create():
            def selector(x):
                return scheduler.create_cold_observable(send(100, 2 * x), send(200, 3 * x), close(300))
            return xs.expand(selector)
        results = scheduler.start(create)

        results.messages.assert_equal(send(550, 1), send(650, 2), send(750, 3), send(750, 4), send(850, 2), send(850, 6), send(850, 6), send(850, 8), send(950, 9), send(950, 12), send(950, 4), send(950, 12), send(950, 12), send(950, 16))
        xs.subscriptions.assert_equal(subscribe(200, 950))

    def test_expand_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(550, 1), send(850, 2), close(950))

        def create():
            def selector(x):
                raise Exception(ex)
            return xs.expand(selector)
        results = scheduler.start(create)

        results.messages.assert_equal(send(550, 1), throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))
