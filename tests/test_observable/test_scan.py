import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestScan(unittest.TestCase):

    def test_scan_seed_never(self):
        scheduler = TestScheduler()
        seed = 42

        def create():
            def func(acc, x):
                return acc + x
            return Observable.never().scan(seed=seed, accumulator=func)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_scan_seed_empty(self):
        scheduler = TestScheduler()
        seed = 42
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.scan(lambda acc, x: acc + x, seed=seed)

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_scan_seed_return(self):
        scheduler = TestScheduler()
        seed = 42
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.scan(lambda acc, x: acc + x, seed=seed)

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value == seed + 2 and results[0].time == 220)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_scan_seed_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        seed = 42
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))

        def create():
            return xs.scan(seed, lambda acc, x: acc + x)

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

    def test_scan_seed_somedata(self):
        scheduler = TestScheduler()
        seed = 1
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

        def create():
            return xs.scan(lambda acc, x: acc + x, seed=seed)

        results = scheduler.start(create).messages
        assert(len(results) == 5)
        assert(results[0].value.kind == 'N' and results[0].value.value == seed + 2 and results[0].time == 210)
        assert(results[1].value.kind == 'N' and results[1].value.value == seed + 2 + 3 and results[1].time == 220)
        assert(results[2].value.kind == 'N' and results[2].value.value == seed + 2 + 3 + 4 and results[2].time == 230)
        assert(results[3].value.kind == 'N' and results[3].value.value == seed + 2 + 3 + 4 + 5 and results[3].time == 240)
        assert(results[4].value.kind == 'C' and results[4].time == 250)

    def test_scan_noseed_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().scan(lambda acc, x: acc + x)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_scan_noseed_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.scan(lambda acc, x: acc + x)

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_scan_noseed_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            def func(acc, x):
                if acc is None:
                    acc = 0
                return acc + x
            return xs.scan(accumulator=func)

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].time == 220 and results[0].value.value == 2)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_scan_noseed_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))

        def create():
            def func(acc, x):
                if acc is None:
                    acc = 0

                return acc + x
            return xs.scan(func)
        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'E' and results[0].time == 250 and results[0].value.exception == ex)

    def test_scan_noseed_somedata(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

        def create():
            def func(acc, x):
                if acc is None:
                    acc = 0
                return acc + x
            return xs.scan(func)

        results = scheduler.start(create).messages
        assert(len(results) == 5)
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'N' and results[1].time == 220 and results[1].value.value == 2 + 3)
        assert(results[2].value.kind == 'N' and results[2].time == 230 and results[2].value.value == 2 + 3 + 4)
        assert(results[3].value.kind == 'N' and results[3].time == 240 and results[3].value.value == 2 + 3 + 4 + 5)
        assert(results[4].value.kind == 'C' and results[4].time == 250)

