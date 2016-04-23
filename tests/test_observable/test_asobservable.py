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


class TestAsObservable(unittest.TestCase):
    def test_as_observable_hides(self):
        some_observable = Observable.empty()
        assert(some_observable.as_observable() != some_observable)

    def test_as_observable_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().as_observable()
        results = scheduler.start(create)

        results.messages.assert_equal()

    def test_as_observable_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.as_observable()

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_as_observable_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))

        def create():
            return xs.as_observable()

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

    def test_as_observable_Return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.as_observable()

        results = scheduler.start(create).messages
        self.assertEqual(2, len(results))
        assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 220)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_as_observable_isnoteager(self):
        scheduler = TestScheduler()
        subscribed = [False]

        def subscribe(obs):
            subscribed[0] = True
            disp = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250)).subscribe(obs)

            def func():
                return disp.dispose()
            return func

        xs = Observable.create(subscribe)
        xs.as_observable()
        assert(not subscribed[0])

        def create():
            return xs.as_observable()
        scheduler.start(create)

        assert(subscribed[0])


