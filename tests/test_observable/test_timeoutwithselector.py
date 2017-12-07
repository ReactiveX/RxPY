import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            send(310, 1),
            send(350, 2),
            send(420, 3),
            close(450)
        )
        ys = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: ys)

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(310, 1),
            send(350, 2),
            send(420, 3),
            close(450)
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
            send(310, 1),
            send(350, 2),
            send(420, 3),
            close(450)
        )
        ys = scheduler.create_cold_observable(
            send(100, 'boo!')
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
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(send(50, 'boo!'))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(send(310, 1).equals(results.messages[0]))
        assert(send(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_timeout_by_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(close(50))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        self.assertEqual(3, len(results.messages))
        assert(send(310, 1).equals(results.messages[0]))
        assert(send(350, 2).equals(results.messages[1]))
        assert(results.messages[2].time == 400 and results.messages[2].value.exception)
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_timeout_by_completion(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
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
            send(310, 1),
            send(350, 2),
            send(420, 3),
            throw(420, ex)
        )
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420))

    def test_timeout_duration_simple_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(throw(50, ex))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(send(310, 1), send(350, 2), throw(400, ex))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 400))

    def test_timeout_duration_simple_first_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable(throw(50, ex))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(throw(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))
        ys.subscriptions.assert_equal(subscribe(200, 250))
        zs.subscriptions.assert_equal()

    def test_timeout_duration_simple_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), throw(450, ex))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        results.messages.assert_equal(send(310, 1), send(350, 2), send(420, 3), throw(450, ex))
        xs.subscriptions.assert_equal(subscribe(200, 450))
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal(subscribe(310, 350), subscribe(350, 420), subscribe(420, 450))
