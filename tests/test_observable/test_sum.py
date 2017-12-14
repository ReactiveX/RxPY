import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSum(unittest.TestCase):
    def test_sum_int32_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.sum()

        res = scheduler.start(create=create).messages
        assert res == [send(250, 0), close(250)]

    def test_sum_int32_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        assert res == [send(250, 2), close(250)]

    def test_sum_int32_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), close(250))
        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        assert res == [send(250, 2 + 3 + 4), close(250)]

    def test_sum_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))

        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_sum_int32_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1))
        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        assert res == []

    def test_sum_selector_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, "fo"), send(220, "b"), send(230, "qux"), close(240))

        def create():
            return xs.sum(lambda x: len(x))

        res = scheduler.start(create=create)

        assert res.messages == [send(240, 6), close(240)]
        assert xs.subscriptions == [subscribe(200, 240)]
