import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestTakeLast(unittest.TestCase):
    def test_takelast_zero1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            close(230))

        def create():
            return xs.take_last_with_time(0)

        res = scheduler.start(create)

        res.messages.assert_equal(close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_takelast_zero2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(230))

        def create():
            return xs.take_last_with_time(0)

        res = scheduler.start(create)

        res.messages.assert_equal(close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_takelast_some1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(240))

        def create():
            return xs.take_last_with_time(25)

        res = scheduler.start(create)

        res.messages.assert_equal(send(240, 2), send(240, 3), close(240))
        xs.subscriptions.assert_equal(subscribe(200, 240))

    def test_takelast_some2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(300))

        def create():
            return xs.take_last_with_time(25)

        res = scheduler.start(create)

        res.messages.assert_equal(close(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))

    def test_takelast_some3(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), send(270, 7), send(280, 8), send(290, 9), close(300))

        def create():
            return xs.take_last_with_time(45)

        res = scheduler.start(create)

        res.messages.assert_equal(send(300, 6), send(300, 7), send(300, 8), send(300, 9), close(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))

    def test_takelast_some4(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(250, 3), send(280, 4), send(290, 5), send(300, 6), close(350))

        def create():
            return xs.take_last_with_time(25)

        res = scheduler.start(create)

        res.messages.assert_equal(close(350))
        xs.subscriptions.assert_equal(subscribe(200, 350))

    def test_takelast_all(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.take_last_with_time(50)

        res = scheduler.start(create)

        res.messages.assert_equal(send(230, 1), send(230, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_takelast_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(210, ex))

        def create():
            return xs.take_last_with_time(50)

        res = scheduler.start(create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_takelast_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.take_last_with_time(50)

        res = scheduler.start(create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

