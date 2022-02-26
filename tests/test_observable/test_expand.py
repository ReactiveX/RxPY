import unittest

from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

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


class TestExpand(unittest.TestCase):
    def test_expand_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(300))

        def create():
            def mapper():
                return scheduler.create_cold_observable(
                    on_next(100, 1), on_next(200, 2), on_completed(300)
                )

            return xs.pipe(ops.expand(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_completed(300)]
        assert xs.subscriptions == [subscribe(200, 300)]

    def test_expand_error(self):
        scheduler = TestScheduler()
        ex = "ex"
        xs = scheduler.create_hot_observable(on_error(300, ex))

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(
                    on_next(100 + x, 2 * x),
                    on_next(200 + x, 3 * x),
                    on_completed(300 + x),
                )

            return xs.pipe(ops.expand(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_error(300, ex)]
        assert xs.subscriptions == [subscribe(200, 300)]

    def test_expand_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(
                    on_next(100 + x, 2 * x),
                    on_next(200 + x, 3 * x),
                    on_completed(300 + x),
                )

            return xs.pipe(ops.expand(mapper))

        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_expand_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(550, 1), on_next(850, 2), on_completed(950)
        )

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(
                    on_next(100, 2 * x), on_next(200, 3 * x), on_completed(300)
                )

            return xs.pipe(ops.expand(mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(550, 1),
            on_next(650, 2),
            on_next(750, 3),
            on_next(750, 4),
            on_next(850, 2),
            on_next(850, 6),
            on_next(850, 6),
            on_next(850, 8),
            on_next(950, 9),
            on_next(950, 12),
            on_next(950, 4),
            on_next(950, 12),
            on_next(950, 12),
            on_next(950, 16),
        ]
        assert xs.subscriptions == [subscribe(200, 950)]

    def test_expand_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(550, 1), on_next(850, 2), on_completed(950)
        )

        def create():
            def mapper(x):
                raise Exception(ex)

            return xs.pipe(ops.expand(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(550, 1), on_error(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]
