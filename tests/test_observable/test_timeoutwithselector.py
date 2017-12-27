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

        assert results.messages == [
            send(310, 1),
            send(350, 2),
            send(420, 3),
            close(450)]
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
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(200, 300)]
        assert zs.subscriptions == []

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
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

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
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_timeout_by_completion(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            def mapper(x):
                if x < 3:
                    return zs
                else:
                    raise Exception(ex)

            return xs.timeout_with_selector(ys, mapper)

        results = scheduler.start(create)

        assert results.messages == [
            send(310, 1),
            send(350, 2),
            send(420, 3),
            throw(420, ex)]
        assert xs.subscriptions == [subscribe(200, 420)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 420)]

    def test_timeout_duration_simple_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable(throw(50, ex))

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        assert results.messages == [send(310, 1), send(350, 2), throw(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 400)]

    def test_timeout_duration_simple_first_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable(throw(50, ex))
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        assert results.messages == [throw(250, ex)]
        assert xs.subscriptions == [subscribe(200, 250)]
        assert ys.subscriptions == [subscribe(200, 250)]
        assert zs.subscriptions == []

    def test_timeout_duration_simple_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), throw(450, ex))
        ys = scheduler.create_cold_observable()
        zs = scheduler.create_cold_observable()

        def create():
            return xs.timeout_with_selector(ys, lambda _: zs)
        results = scheduler.start(create)

        assert results.messages == [send(310, 1), send(350, 2), send(420, 3), throw(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == [subscribe(310, 350), subscribe(350, 420), subscribe(420, 450)]
