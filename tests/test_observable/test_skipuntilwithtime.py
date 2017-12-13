import unittest
from datetime import datetime

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipUntilWithTIme(unittest.TestCase):

    def test_skipuntil_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_until_with_time(datetime.utcfromtimestamp(0))
        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_skipuntil_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_until_with_time(datetime.utcfromtimestamp(250))

        res = scheduler.start(create)

        res.messages.assert_equal(close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_skipuntil_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(210, ex))

        def create():
            return xs.skip_until_with_time(datetime.utcfromtimestamp(250))

        res = scheduler.start(create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_skipuntil_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.skip_until_with_time(datetime.utcfromtimestamp(250))

        res = scheduler.start(create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_skipuntil_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            send(250, 5),
            send(260, 6),
            close(270))

        def create():
            return xs.skip_until_with_time(
                datetime.utcfromtimestamp(0.215)
            ).skip_until_with_time(
                datetime.utcfromtimestamp(0.230)
            )

        res = scheduler.start(create)

        res.messages.assert_equal(
            send(240, 4),
            send(250, 5),
            send(260, 6),
            close(270))
        xs.subscriptions.assert_equal(subscribe(200, 270))

    def test_skipuntil_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))

        def create():
            return xs.skip_until_with_time(
                datetime.utcfromtimestamp(0.230)
            ).skip_until_with_time(
                datetime.utcfromtimestamp(0.215))

        res = scheduler.start(create)

        res.messages.assert_equal(send(240, 4), send(250, 5), send(260, 6), close(270))
        xs.subscriptions.assert_equal(subscribe(200, 270))

