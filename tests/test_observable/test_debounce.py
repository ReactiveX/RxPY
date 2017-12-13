import unittest

from rx import Observable
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


class TestDebounce(unittest.TestCase):
    def test_debounce_timespan_allpass(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(200, 2), send(250, 3), send(300, 4), send(350, 5), send(400, 6), send(450, 7), send(500, 8), close(550))

        def create():
            return xs.debounce(40)

        results = scheduler.start(create)

        assert results.messages == [send(290, 3), send(340, 4), send(390, 5), send(440, 6), send(490, 7), send(540, 8), close(550)]

    def test_debounce_timespan_allpass_error_end(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(200, 2), send(250, 3), send(300, 4), send(350, 5), send(400, 6), send(450, 7), send(500, 8), throw(550, ex))

        def create():
            return xs.debounce(40)

        results = scheduler.start(create)
        assert results.messages == [send(290, 3), send(340, 4), send(390, 5), send(440, 6), send(490, 7), send(540, 8), throw(550, ex)]

    def test_debounce_timespan_alldrop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(200, 2), send(250, 3), send(300, 4), send(350, 5), send(400, 6), send(450, 7), send(500, 8), close(550))

        def create():
            return xs.debounce(60)

        results = scheduler.start(create)
        assert results.messages == [send(550, 8), close(550)]

    def test_debounce_timespan_alldrop_error_end(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(200, 2), send(250, 3), send(300, 4), send(350, 5), send(400, 6), send(450, 7), send(500, 8), throw(550, ex))

        def create():
            return xs.debounce(60)

        results = scheduler.start(create)
        assert results.messages == [throw(550, ex)]

    def test_debounce_timespan_some_drop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(370, 4), send(421, 5), send(480, 6), send(490, 7), send(500, 8), close(600))

        def create():
            return xs.debounce(50)

        results = scheduler.start(create)
        assert results.messages == [send(300, 2), send(420, 4), send(471, 5), send(550, 8), close(600)]

    def test_debounce_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty().debounce(10)

        results = scheduler.start(create)

        assert results.messages == [close(200)]

    def test_debounce_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw_exception(ex).debounce(10)

        results = scheduler.start(create)
        assert results.messages == [throw(200, ex)]

    def test_debounce_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().debounce(10)

        results = scheduler.start(create)
        assert results.messages == []

    def test_debounce_duration_delay_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, -1), send(250, 0), send(280, 1), send(310, 2), send(350, 3), send(400, 4), close(550))
        ys = [scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99))]

        def create():
            def selector(x):
                return ys[x]

            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 20, 0), send(280 + 20, 1), send(310 + 20, 2), send(350 + 20, 3), send(400 + 20, 4), close(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 280 + 20)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 350 + 20)]
        assert ys[4].subscriptions == [subscribe(400, 400 + 20)]

    def test_debounce_duration_throttle_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, -1), send(250, 0), send(280, 1), send(310, 2), send(350, 3), send(400, 4), close(550))
        ys = [scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(40, 42), send(45, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(60, 42), send(65, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99))]

        def create():
            def selector(x):
                return ys[x]
            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 20, 0), send(310 + 20, 2), send(400 + 20, 4), close(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 310)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 400)]
        assert ys[4].subscriptions == [subscribe(400, 400 + 20)]

    def test_debounce_duration_early_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, -1), send(250, 0), send(280, 1), send(310, 2), send(350, 3), send(400, 4), close(410))
        ys = [scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(40, 42), send(45, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99)), scheduler.create_cold_observable(send(60, 42), send(65, 99)), scheduler.create_cold_observable(send(20, 42), send(25, 99))]

        def create():
            def selector(x):
                return ys[x]
            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 20, 0), send(310 + 20, 2), send(410, 4), close(410)]
        assert xs.subscriptions == [subscribe(200, 410)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 310)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 400)]
        assert ys[4].subscriptions == [subscribe(400, 410)]

    def test_debounce_duration_inner_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))
        ex = 'ex'

        def create():
            def selector(x):
                if x < 4:
                    return scheduler.create_cold_observable(send(x * 10, "Ignore"), send(x * 10 + 5, "Aargh!"))
                else:
                    return scheduler.create_cold_observable(throw(x * 10, ex))

            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 2 * 10, 2), send(350 + 3 * 10, 3), throw(450 + 4 * 10, ex)]
        assert xs.subscriptions == [subscribe(200, 490)]

    def test_debounce_duration_outer_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), throw(460, ex))

        def create():
            def selector(x):
                return scheduler.create_cold_observable(send(x * 10, "Ignore"), send(x * 10 + 5, "Aargh!"))
            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 2 * 10, 2), send(350 + 3 * 10, 3), throw(460, ex)]
        assert xs.subscriptions == [subscribe(200, 460)]

    def test_debounce_duration_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            def selector(x):
                if x < 4:
                    return scheduler.create_cold_observable(send(x * 10, "Ignore"), send(x * 10 + 5, "Aargh!"))
                else:
                    _raise(ex)

            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 2 * 10, 2), send(350 + 3 * 10, 3), throw(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_debounce_duration_inner_done_delay_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            def selector(x):
                return scheduler.create_cold_observable(close(x * 10))
            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 2 * 10, 2), send(350 + 3 * 10, 3), send(450 + 4 * 10, 4), close(550)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_debounce_duration_inner_done_throttle_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(280, 3), send(300, 4), send(400, 5), send(410, 6), close(550))

        def create():
            def selector(x):
                return scheduler.create_cold_observable(close(x * 10))
            return xs.throttle_with_selector(selector)

        results = scheduler.start(create)

        assert results.messages == [send(250 + 2 * 10, 2), send(300 + 4 * 10, 4), send(410 + 6 * 10, 6), close(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
