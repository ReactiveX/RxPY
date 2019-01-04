import unittest

from rx import empty, never, throw, operators as _
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


class TestDebounce(unittest.TestCase):
    def test_debounce_timespan_allpass(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(
            300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_completed(550))

        def create():
            return xs.pipe(_.debounce(40))

        results = scheduler.start(create)

        assert results.messages == [on_next(290, 3), on_next(340, 4), on_next(
            390, 5), on_next(440, 6), on_next(490, 7), on_next(540, 8), on_completed(550)]

    def test_debounce_timespan_allpass_error_end(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(
            300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_error(550, ex))

        def create():
            return xs.pipe(_.debounce(40))

        results = scheduler.start(create)
        assert results.messages == [on_next(290, 3), on_next(340, 4), on_next(
            390, 5), on_next(440, 6), on_next(490, 7), on_next(540, 8), on_error(550, ex)]

    def test_debounce_timespan_alldrop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(
            300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_completed(550))

        def create():
            return xs.pipe(_.debounce(60))

        results = scheduler.start(create)
        assert results.messages == [on_next(550, 8), on_completed(550)]

    def test_debounce_timespan_alldrop_error_end(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(200, 2), on_next(250, 3), on_next(
            300, 4), on_next(350, 5), on_next(400, 6), on_next(450, 7), on_next(500, 8), on_error(550, ex))

        def create():
            return xs.pipe(_.debounce(60))

        results = scheduler.start(create)
        assert results.messages == [on_error(550, ex)]

    def test_debounce_timespan_some_drop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(250, 2), on_next(350, 3), on_next(
            370, 4), on_next(421, 5), on_next(480, 6), on_next(490, 7), on_next(500, 8), on_completed(600))

        def create():
            return xs.pipe(_.debounce(50))

        results = scheduler.start(create)
        assert results.messages == [on_next(300, 2), on_next(
            420, 4), on_next(471, 5), on_next(550, 8), on_completed(600)]

    def test_debounce_empty(self):
        scheduler = TestScheduler()

        def create():
            return empty().pipe(_.debounce(10))

        results = scheduler.start(create)

        assert results.messages == [on_completed(200)]

    def test_debounce_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return throw(ex).pipe(_.debounce(10))

        results = scheduler.start(create)
        assert results.messages == [on_error(200, ex)]

    def test_debounce_never(self):
        scheduler = TestScheduler()

        def create():
            return never().pipe(_.debounce(10))

        results = scheduler.start(create)
        assert results.messages == []

    def test_debounce_duration_delay_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, -1),
            on_next(250, 0),
            on_next(280, 1),
            on_next(310, 2),
            on_next(350, 3),
            on_next(400, 4),
            on_completed(550))
        ys = [scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(
            on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99))]

        def create():
            def mapper(x):
                return ys[x]

            return xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 20, 0), on_next(280 + 20, 1), on_next(310 + 20, 2),
                                    on_next(350 + 20, 3), on_next(400 + 20, 4), on_completed(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 280 + 20)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 350 + 20)]
        assert ys[4].subscriptions == [subscribe(400, 400 + 20)]

    def test_debounce_duration_throttle_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, -1), on_next(250, 0), on_next(280, 1),
                                             on_next(310, 2), on_next(350, 3), on_next(400, 4), on_completed(550))
        ys = [scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(40, 42), on_next(45, 99)), scheduler.create_cold_observable(
            on_next(20, 42), on_next(25, 99)), scheduler.create_cold_observable(on_next(60, 42), on_next(65, 99)), scheduler.create_cold_observable(on_next(20, 42), on_next(25, 99))]

        def create():
            def mapper(x):
                return ys[x]
            return xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 20, 0), on_next(310 + 20, 2), on_next(400 + 20, 4), on_completed(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 310)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 400)]
        assert ys[4].subscriptions == [subscribe(400, 400 + 20)]

    def test_debounce_duration_early_completion(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, -1),
            on_next(250, 0),
            on_next(280, 1),
            on_next(310, 2),
            on_next(350, 3),
            on_next(400, 4),
            on_completed(410))
        ys = [
            scheduler.create_cold_observable(
                on_next(20, 42),
                on_next(25, 99)),
            scheduler.create_cold_observable(
                on_next(40, 42),
                on_next(45, 99)),
            scheduler.create_cold_observable(
                on_next(20, 42),
                on_next(25, 99)),
            scheduler.create_cold_observable(
                on_next(60, 42),
                on_next(65, 99)),
            scheduler.create_cold_observable(
                on_next(20, 42),
                on_next(25, 99))
        ]

        def create():
            def mapper(x):
                return ys[x]
            return xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 20, 0), on_next(310 + 20, 2), on_next(410, 4), on_completed(410)]
        assert xs.subscriptions == [subscribe(200, 410)]
        assert ys[0].subscriptions == [subscribe(250, 250 + 20)]
        assert ys[1].subscriptions == [subscribe(280, 310)]
        assert ys[2].subscriptions == [subscribe(310, 310 + 20)]
        assert ys[3].subscriptions == [subscribe(350, 400)]
        assert ys[4].subscriptions == [subscribe(400, 410)]

    def test_debounce_duration_inner_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(
            250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))
        ex = 'ex'

        def create():
            def mapper(x):
                if x < 4:
                    return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
                else:
                    return scheduler.create_cold_observable(on_error(x * 10, ex))

            return xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(450 + 4 * 10, ex)]
        assert xs.subscriptions == [subscribe(200, 490)]

    def test_debounce_duration_outer_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(
            250, 2), on_next(350, 3), on_next(450, 4), on_error(460, ex))

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
            return  xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(460, ex)]
        assert xs.subscriptions == [subscribe(200, 460)]

    def test_debounce_duration_mapper_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(
            250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))

        def create():
            def mapper(x):
                if x < 4:
                    return scheduler.create_cold_observable(on_next(x * 10, "Ignore"), on_next(x * 10 + 5, "Aargh!"))
                else:
                    _raise(ex)

            return  xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 2 * 10, 2), on_next(350 + 3 * 10, 3), on_error(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_debounce_duration_inner_done_delay_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(
            250, 2), on_next(350, 3), on_next(450, 4), on_completed(550))

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(on_completed(x * 10))
            return  xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(250 + 2 * 10, 2),
            on_next(350 + 3 * 10, 3),
            on_next(450 + 4 * 10, 4),
            on_completed(550)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_debounce_duration_inner_done_throttle_behavior(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(400, 5),
            on_next(410, 6),
            on_completed(550))

        def create():
            def mapper(x):
                return scheduler.create_cold_observable(on_completed(x * 10))
            return  xs.pipe(_.throttle_with_mapper(mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(250 + 2 * 10, 2), on_next(300 + 4 * 10, 4),
                                    on_next(410 + 6 * 10, 6), on_completed(550)]
        assert xs.subscriptions == [subscribe(200, 550)]
