import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipLastWithTime(unittest.TestCase):
    def test_skiplast_zero1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_last_with_time(0)
        res = scheduler.start(create)

        assert res.messages == [send(210, 1), send(220, 2), close(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_zero2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(230))

        def create():
            return xs.skip_last_with_time(0)

        res = scheduler.start(create)

        assert res.messages == [send(210, 1), send(220, 2), send(230, 3), close(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_some1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(230))

        def create():
            return xs.skip_last_with_time(15)

        res = scheduler.start(create)

        assert res.messages == [send(230, 1), close(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_some2(self):
        scheduler = TestScheduler()

        def create():
            return xs.skip_last_with_time(45)

        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), send(270, 7), send(280, 8), send(290, 9), close(300))
        res = scheduler.start(create)

        assert res.messages == [send(260, 1), send(270, 2), send(280, 3), send(290, 4), send(300, 5), close(300)]
        assert xs.subscriptions == [subscribe(200, 300)]

    def test_skiplast_all(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))

        def create():
            return xs.skip_last_with_time(45)
        res = scheduler.start(create)

        assert res.messages == [close(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skiplast_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(210, ex))

        def create():
            return xs.skip_last_with_time(45)
        res = scheduler.start(create)

        assert res.messages == [throw(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_skiplast_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.skip_last_with_time(50)

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]
