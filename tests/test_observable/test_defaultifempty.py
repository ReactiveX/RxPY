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
    def test_default_if_empty_non_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), close(420))

        def create():
            return xs.default_if_empty()

        results = scheduler.start(create)

        assert results.messages == [send(280, 42), send(360, 43), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_non_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), close(420))

        def create():
            return xs.default_if_empty(-1)

        results = scheduler.start(create)

        assert results.messages == [send(280, 42), send(360, 43), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(420))

        def create():
            return xs.default_if_empty(None)

        results = scheduler.start(create)

        assert results.messages == [send(420, None), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(420))

        def create():
            return xs.default_if_empty(-1)
        results = scheduler.start(create)

        assert results.messages == [send(420, -1), close(420)]
        assert xs.subscriptions == [subscribe(200, 420)]
