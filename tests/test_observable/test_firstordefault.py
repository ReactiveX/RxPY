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


class TestFirst_or_default(unittest.TestCase):
    def test_first_or_default_async_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))
        def create():
            return xs.first_or_default(None, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(250, 0), close(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_first_or_default_async_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

        def create():
            return xs.first_or_default(None, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(210, 2), close(210))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_or_default_async_many(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), close(250))

        def create():
            return xs.first_or_default(None, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(210, 2), close(210))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_or_default_async_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))

        def create():
            return xs.first_or_default(None, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_or_default_async_predicate(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            def predicate(x):
                return x % 2 == 1

            return xs.first_or_default(predicate, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(220, 3), close(220))
        xs.subscriptions.assert_equal(subscribe(200, 220))

    def test_first_or_default_async_predicate_none(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            def predicate(x):
                return x > 10

            return xs.first_or_default(predicate, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(250, 0), close(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))


    def test_first_or_default_async_predicate_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), throw(220, ex))

        def create():
            def predicate(x):
                return x % 2 == 1

            return xs.first_or_default(predicate, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(throw(220, ex))
        xs.subscriptions.assert_equal(subscribe(200, 220))


    def test_first_or_default_async_predicate_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            def predicate(x):
                if x < 4:
                    return False
                else:
                    raise Exception(ex)

            return xs.first_or_default(predicate, 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(throw(230, ex))
        xs.subscriptions.assert_equal(subscribe(200, 230))

