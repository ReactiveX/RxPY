from datetime import datetime
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


class TestTakeUntilWithTime(unittest.TestCase):

    def test_takeuntil_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.take_until_with_time(datetime.utcfromtimestamp(0))

        res = scheduler.start(create)

        res.messages.assert_equal(close(200))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    def test_takeuntil_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            close(230)
        )

        def create():
            dt = datetime.utcfromtimestamp(250)
            return xs.take_until_with_time(dt, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_takeuntil_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(210, ex))
        def create():
            dt = datetime.utcfromtimestamp(0.250)
            return xs.take_until_with_time(dt, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_takeuntil_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            dt = datetime.utcfromtimestamp(0.250)
            return xs.take_until_with_time(dt, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(close(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_takeuntil_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            send(250, 5),
            send(260, 6),
            close(270)
        )
        def create():
            dt235 = datetime.utcfromtimestamp(0.235)
            dt255 = datetime.utcfromtimestamp(0.255)
            return xs.take_until_with_time(dt255, scheduler).take_until_with_time(dt235, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))

    def test_takeuntil_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            send(250, 5),
            send(260, 6),
            close(270)
        )

        def create():
            dt235 = datetime.utcfromtimestamp(0.235)
            dt255 = datetime.utcfromtimestamp(0.255)
            return xs.take_until_with_time(dt235, scheduler).take_until_with_time(dt255, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))
