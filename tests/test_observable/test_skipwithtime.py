import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipWithTime(unittest.TestCase):
    def test_skip_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))

        def create():
            return xs.skip_with_time(0)

        res = scheduler.start(create)

        assert res.messages == [on_next(210, 1), on_next(220, 2), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skip_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))

        def create():
            return xs.skip_with_time(15)

        res = scheduler.start(create)

        assert res.messages == [on_next(220, 2), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skip_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))

        def create():
            return xs.skip_with_time(50)

        res = scheduler.start(create)

        assert res.messages == [on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_skip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(210, ex))

        def create():
            return xs.skip_with_time(50)

        res = scheduler.start(create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_skip_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.skip_with_time(50)

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_skip_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))

        def create():
            return xs.skip_with_time(15).skip_with_time(30)

        res = scheduler.start(create)

        assert res.messages == [on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270)]
        assert xs.subscriptions == [subscribe(200, 270)]

    def test_skip_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))

        def create():
            return xs.skip_with_time(30).skip_with_time(15)

        res = scheduler.start(create)

        assert res.messages == [on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270)]
        assert xs.subscriptions == [subscribe(200, 270)]
