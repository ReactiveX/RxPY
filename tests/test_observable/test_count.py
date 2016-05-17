import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestCount(unittest.TestCase):
    def test_count_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
        res = scheduler.start(create=lambda: xs.count()).messages
        res.assert_equal(on_next(250, 0), on_completed(250))

    def test_count_empty_ii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.count()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 1), on_completed(250))

    def test_count_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
        res = scheduler.start(create=lambda: xs.count()).messages
        res.assert_equal(on_next(250, 3), on_completed(250))

    def test_count_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
        res = scheduler.start(create=lambda: xs.count()).messages
        res.assert_equal(on_error(210, ex))

    def test_count_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))
        res = scheduler.start(create=lambda: xs.count()).messages
        res.assert_equal()

    def test_count_predicate_empty_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.count(lambda _: True)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 0), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_empty_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.count(lambda _: False)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 0), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_return_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.count(lambda _: True)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 1), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_return_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.count(lambda _: False)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 0), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_some_all(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))

        def create():
            return xs.count(lambda x: x < 10)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 3), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_some_none(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))

        def create():
            return xs.count(lambda x: x > 10)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 0), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_some_even(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))

        def create():
            return xs.count(lambda x: x % 2 == 0)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(250, 2), on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_count_predicate_throw_true(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.count(lambda _: True)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_count_predicate_throw_false(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.count(lambda _: False)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_count_predicate_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))

        def create():
            return xs.count(lambda _: True)

        res = scheduler.start(create=create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_count_predicate_predicate_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_completed(240))

        def create():
            def predicate(x):
                if x == 3:
                    raise Exception(ex)
                else:
                    return True

            return xs.count(predicate)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(230, ex))
        xs.subscriptions.assert_equal(subscribe(200, 230))
