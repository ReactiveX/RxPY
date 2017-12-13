import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestTakeWithTime(unittest.TestCase):

    def test_take_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            close(230))

        def create():
            return xs.take_with_time(0)
        res = scheduler.start(create)

        res.messages.assert_equal(close(200))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    def test_take_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(240))

        def create():
            return xs.take_with_time(25)
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), close(225))
        xs.subscriptions.assert_equal(subscribe(200, 225))

    def test_take_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.take_with_time(50)
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_take_Error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_hot_observable(throw(210, ex))

        def create():
            return xs.take_with_time(50)

        res = scheduler.start(create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_take_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.take_with_time(50)
        res = scheduler.start(create)

        res.messages.assert_equal(close(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_take_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))

        def create():
            return xs.take_with_time(55).take_with_time(35)

        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))

    def test_take_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))

        def create():
            return xs.take_with_time(35).take_with_time(55)

        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))
