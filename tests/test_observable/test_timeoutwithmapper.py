import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

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


class TestTimeoutWithSelector(unittest.TestCase):
    def test_timeout_duration_simple_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_completed(450)
        )
        ys = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: ys))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_completed(450)]
        assert xs.subscriptions == [
            subscribe(200, 450)]
        assert ys.subscriptions == [
            subscribe(200, 310),
            subscribe(310, 350),
            subscribe(350, 420),
            subscribe(420, 450)]

    def test_timeout_duration_simple_timeoutfirst(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_completed(450)
        )
        ys = scheduler.create_cold_observable(
            on_next(100, 'boo!')
        )
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))

        results = scheduler.start(create)

        self.assertEqual(1, len(results.messages))
        assert(results.messages[0].time == 300 and results.messages[0].value.exception)
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(200, 300)]
        assert zs.subscriptions == []

    def test_timeout_duration_simple_timeout_later(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_next(50, 'boo!'))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(on_next(310, 1).equals(results.messages[0]))
        assert(on_next(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_timeout_by_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_completed(50))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(on_next(310, 1).equals(results.messages[0]))
        assert(on_next(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_timeout_by_completion(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            def mapper(x):
                if x < 3:
                    return zs
                else:
                    raise Exception(ex)

            return xs.pipe(ops.timeout_with_mapper(ys, mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_error(420, ex)]
        assert xs.subscriptions == [subscribe(200, 420)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 420)]

    def test_timeout_duration_simple_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_error(50, ex))

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))
        results = scheduler.start(create)

        assert results.messages == [on_next(310, 1), on_next(350, 2), on_error(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_first_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable(on_error(50, ex))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))
        results = scheduler.start(create)

        assert results.messages == [on_error(250, ex)]
        assert xs.subscriptions == [subscribe(200, 250)]
        assert ys.subscriptions == [subscribe(200, 250)]
        assert zs.subscriptions == []

    def test_timeout_duration_simple_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            return xs.pipe(ops.timeout_with_mapper(ys, lambda _: zs))
        results = scheduler.start(create)

        assert results.messages == [on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 420), subscribe(420, 450)]
