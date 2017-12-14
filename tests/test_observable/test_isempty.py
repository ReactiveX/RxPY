import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestIsEmpty(unittest.TestCase):
    def test_is_empty_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.is_empty()

        res = scheduler.start(create=create).messages
        assert res == [send(250, True), close(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_is_empty_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        assert res == [send(210, False), close(210)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_is_empty_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))

        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_is_empty_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1))
        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        assert res == []
        assert xs.subscriptions == [subscribe(200, 1000)]

