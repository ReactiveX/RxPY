import unittest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestSingleOrDefault(unittest.TestCase):
    def test_single_or_default_async_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.pipe(ops.single_or_default(None, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(250, 0), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_single_or_default_async_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1), on_next(210, 2), on_completed(250)
        )

        def create():
            return xs.pipe(ops.single_or_default(None, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(250, 2), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_single_or_default_async_many(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250)
        )

        def create():
            return xs.pipe(ops.single_or_default(None, 0))

        res = scheduler.start(create=create)

        def predicate(e):
            return not e is None

        # assert res.messages == [on_error(220, predicate)]
        assert [on_error(220, predicate)] == res.messages
        assert xs.subscriptions == [subscribe(200, 220)]

    def test_single_or_default_async_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.pipe(ops.single_or_default(None, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_single_or_default_async_predicate(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            def predicate(x):
                return x % 2 == 1

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        def predicate(e):
            return not e is None

        assert [on_error(240, predicate)] == res.messages
        assert xs.subscriptions == [subscribe(200, 240)]

    def test_single_or_default_async_predicate_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            def predicate(x):
                return x % 2 == 1

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(250, 0), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_single_or_default_async_predicate_one(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            def predicate(x):
                return x == 4

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(250, 4), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_single_or_default_async_predicate_none(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            def predicate(x):
                return x > 10

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(250, 0), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_single_or_default_async_predicate_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            def predicate(x):
                return x > 10

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_single_or_default_async_predicate_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            def predicate(x):
                if x < 4:
                    return False
                else:
                    raise Exception(ex)

            return xs.pipe(ops.single_or_default(predicate, 0))

        res = scheduler.start(create=create)

        assert res.messages == [on_error(230, ex)]
        assert xs.subscriptions == [subscribe(200, 230)]
