import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSum(unittest.TestCase):
    def test_sum_int32_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.sum()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 0), on_completed(250))

    def test_sum_int32_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 2), on_completed(250))

    def test_sum_int32_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 2 + 3 + 4), on_completed(250))

    def test_sum_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_sum_int32_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))
        def create():
            return xs.sum()
        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_sum_selector_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, "fo"), on_next(220, "b"), on_next(230, "qux"), on_completed(240))

        def create():
            return xs.sum(lambda x: len(x))

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(240, 6), on_completed(240))
        xs.subscriptions.assert_equal(subscribe(200, 240))
