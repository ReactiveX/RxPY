import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSome(unittest.TestCase):

    def test_some_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_some_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(210, True), on_completed(210))

    def test_some_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()
        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_some_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_some_predicate_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_some_predicate_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(210, True), on_completed(210))

    def test_some_predicate_return_not_match(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, -2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_some_predicate_some_none_match(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, -2), on_next(220, -3), on_next(230, -4), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, False), on_completed(250))

    def test_some_predicate_some_match(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, -2), on_next(220, 3), on_next(230, -4), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(220, True), on_completed(220))

    def test_some_predicate_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)
        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_some_predicate_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal()
