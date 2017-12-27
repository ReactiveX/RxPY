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


class TestDelayWithSelector(unittest.TestCase):
    # Delay with mapper
    def test_delay_duration_simple1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 10), send(220, 30), send(230, 50), send(240, 35), send(250, 20), close(260))

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(send(x, '!'))

            return xs.delay_with_selector(mapper)

        results = scheduler.start(create)

        assert results.messages == [send(210 + 10, 10), send(220 + 30, 30), send(250 + 20, 20), send(240 + 35, 35), send(230 + 50, 50), close(280)]
        assert xs.subscriptions == [subscribe(200, 260)]

    def test_delay_duration_simple2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), send(250, 6), close(300))
        ys = scheduler.create_cold_observable(send(10, '!'))

        def create():
            return xs.delay_with_selector(lambda _: ys)

        results = scheduler.start(create)

        assert results.messages == [send(210 + 10, 2), send(220 + 10, 3), send(230 + 10, 4), send(240 + 10, 5), send(250 + 10, 6), close(300)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(210, 220), subscribe(220, 230), subscribe(230, 240), subscribe(240, 250), subscribe(250, 260)]

    def test_delay_duration_simple3(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), send(250, 6), close(300))
        ys = scheduler.create_cold_observable(send(100, '!'))

        def create():
            return xs.delay_with_selector(lambda _: ys)

        results = scheduler.start(create)

        assert results.messages == [send(210 + 100, 2), send(220 + 100, 3), send(230 + 100, 4), send(240 + 100, 5), send(250 + 100, 6), close(350)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(210, 310), subscribe(220, 320), subscribe(230, 330), subscribe(240, 340), subscribe(250, 350)]

    def test_delay_duration_simple4_inner_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), send(250, 6), close(300))
        ys = scheduler.create_cold_observable(close(100))

        def create():
            return xs.delay_with_selector(lambda _: ys)

        results = scheduler.start(create)

        assert results.messages == [send(210 + 100, 2), send(220 + 100, 3), send(230 + 100, 4), send(240 + 100, 5), send(250 + 100, 6), close(350)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(210, 310), subscribe(220, 320), subscribe(230, 330), subscribe(240, 340), subscribe(250, 350)]

    def test_delay_duration_dispose1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), send(250, 6), close(300))
        ys = scheduler.create_cold_observable(send(200, '!'))

        def create():
            return xs.delay_with_selector(lambda _: ys)

        results = scheduler.start(create, disposed=425)
        assert results.messages == [send(210 + 200, 2), send(220 + 200, 3)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(210, 410), subscribe(220, 420), subscribe(230, 425), subscribe(240, 425), subscribe(250, 425)]

    def test_delay_duration_dispose2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(400, 3), close(500))
        ys = scheduler.create_cold_observable(send(50, '!'))

        def create():
            return xs.delay_with_selector(lambda _: ys)

        results = scheduler.start(create, disposed=300)
        assert results.messages == [send(210 + 50, 2)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(210, 260)]

