import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMaterialize(unittest.TestCase):

    def test_materialize_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().materialize()

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_materialize_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.materialize()

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'C' and results[0].time == 250)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_materialize_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.materialize()

        results = scheduler.start(create).messages
        assert(len(results) == 3)
        assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'N' and results[0].value.value.value == 2 and results[0].time == 210)
        assert(results[1].value.kind == 'N' and results[1].value.value.kind == 'C' and results[1].time == 250)
        assert(results[2].value.kind == 'C' and results[1].time == 250)

    def test_materialize_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))

        def create():
            return xs.materialize()

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'E' and results[0].value.value.exception == ex)
        assert(results[1].value.kind == 'C')

    def test_materialize_dematerialize_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().materialize().dematerialize()

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_materialize_dematerialize_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_materialize_dematerialize_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 210)
        assert(results[1].value.kind == 'C')

    def test_materialize_dematerialize_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

if __name__ == '__main__':
    unittest.main()
