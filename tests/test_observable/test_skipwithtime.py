import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipWithTime(unittest.TestCase):
    def test_skip_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_with_time(0, scheduler=scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(send(210, 1), send(220, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_skip_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_with_time(15, scheduler=scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(send(220, 2), close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_skip_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_with_time(50, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(close(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_skip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(210, ex))

        def create():
            return xs.skip_with_time(50, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(throw(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_skip_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.skip_with_time(50, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_skip_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))

        def create():
            return xs.skip_with_time(15, scheduler).skip_with_time(30, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(send(240, 4), send(250, 5), send(260, 6), close(270))
        xs.subscriptions.assert_equal(subscribe(200, 270))

    def test_skip_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))

        def create():
            return xs.skip_with_time(30, scheduler).skip_with_time(15, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(send(240, 4), send(250, 5), send(260, 6), close(270))
        xs.subscriptions.assert_equal(subscribe(200, 270))
