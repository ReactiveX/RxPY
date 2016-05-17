import unittest

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
            return xs.timeout_with_selector(ys, lambda _: ys)

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_completed(450)
        )
        xs.subscriptions.assert_equal(
            subscribe(200, 450)
        )
        ys.subscriptions.assert_equal(
            subscribe(200, 310),
            subscribe(310, 350),
            subscribe(350, 420),
            subscribe(420, 450)
        )

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
            return xs.timeout_with_selector(ys, lambda _: zs)

        results = scheduler.start(create)

        self.assertEqual(1, len(results.messages))
        assert(results.messages[0].time == 300 and results.messages[0].value.exception)
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal(subscribe(200, 300))
        zs.subscriptions.assert_equal()

    def test_timeout_duration_simple_timeout_later(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_next(50, 'boo!'))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(on_next(310, 1).equals(results.messages[0]))
        assert(on_next(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_timeout_by_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_completed(50))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(on_next(310, 1).equals(results.messages[0]))
        assert(on_next(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_timeout_by_completion(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            def selector(x):
                if x < 3:
                    return zs
                else:
                    raise Exception(ex)

            return xs.timeout_with_selector(ys, selector)

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(310, 1),
            on_next(350, 2),
            on_next(420, 3),
            on_error(420, ex)
        )
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420))

    def test_timeout_duration_simple_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(on_error(50, ex))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_error(400, ex))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_first_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable(on_error(50, ex))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))
        ys.subscriptions.assert_equal(subscribe(200, 250))
        zs.subscriptions.assert_equal()

    def test_timeout_duration_simple_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_error(450, ex))
        xs.subscriptions.assert_equal(subscribe(200, 450))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420), subscribe(420, 450))
