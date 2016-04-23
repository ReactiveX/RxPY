import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestContains(unittest.TestCase):

    def test_contains_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(42)
        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_contains_return_positive(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(2)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(210, True), on_completed(210))

    def test_contains_return_negative(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(-2)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_contains_some_positive(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(3)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(220, True), on_completed(220))

    def test_contains_some_negative(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(-3)
        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_contains_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.contains(42)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_contains_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(42)

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_contains_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2))

        def create():
            def comparer(a, b):
                raise Exception(ex)

            return xs.contains(42, comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_contains_comparer_contains_value(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 3), on_next(220, 4), on_next(230, 8), on_completed(250))

        def create():
            return xs.contains(42, lambda a, b: a % 2 == b % 2)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(220, True), on_completed(220))

    def test_contains_comparer_does_not_contain_value(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 8), on_completed(250))

        def create():
            return xs.contains(21, lambda a, b: a % 2 == b % 2)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))
