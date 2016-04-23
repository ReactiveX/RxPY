import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestIsEmpty(unittest.TestCase):
    def test_is_empty_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.is_empty()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, True), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_is_empty_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(210, False), on_completed(210))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_is_empty_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_is_empty_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))
        def create():
            return xs.is_empty()
        res = scheduler.start(create=create).messages
        res.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

