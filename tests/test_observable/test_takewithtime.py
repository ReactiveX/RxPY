import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestTakeWithTime(unittest.TestCase):

    def test_take_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_completed(230))

        def create():
            return xs.take_with_time(0, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(on_completed(201))
        xs.subscriptions.assert_equal(subscribe(200, 201))

    def test_take_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))

        def create():
            return xs.take_with_time(25, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(225))
        xs.subscriptions.assert_equal(subscribe(200, 225))

    def test_take_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))

        def create():
            return xs.take_with_time(50, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_take_Error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_hot_observable(on_error(210, ex))

        def create():
            return xs.take_with_time(50, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(on_error(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_take_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            return xs.take_with_time(50, scheduler)
        res = scheduler.start(create)

        res.messages.assert_equal(on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_take_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))

        def create():
            return xs.take_with_time(55, scheduler).take_with_time(35, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))

    def test_take_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))

        def create():
            return xs.take_with_time(35, scheduler).take_with_time(55, scheduler)

        res = scheduler.start(create)

        res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
        xs.subscriptions.assert_equal(subscribe(200, 235))
