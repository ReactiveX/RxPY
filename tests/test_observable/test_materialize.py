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


class TestMaterialize(unittest.TestCase):

    def test_materialize_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().materialize()

        results = scheduler.start(create)
        assert results.messages == []

    def test_materialize_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.materialize()

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'C' and results[0].time == 250)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_materialize_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

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
        xs = scheduler.create_hot_observable(send(150, 1), throw(250, ex))

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
        assert results.messages == []

    def test_materialize_dematerialize_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_materialize_dematerialize_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 2)
        assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 210)
        assert(results[1].value.kind == 'C')

    def test_materialize_dematerialize_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(250, ex))

        def create():
            return xs.materialize().dematerialize()

        results = scheduler.start(create).messages
        assert(len(results) == 1)
        assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

if __name__ == '__main__':
    unittest.main()
