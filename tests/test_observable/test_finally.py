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


class TestFinally(unittest.TestCase):
    def test_finally_only_called_once_empty(self):
        invasserte_count = [0]

        def action():
            invasserte_count[0] += 1
            return invasserte_count
        some_observable = Observable.empty().finally_action(action)

        d = some_observable.subscribe()
        d.dispose()
        d.dispose()
        self.assertEqual(1, invasserte_count[0])

    def test_finally_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
        invasserted = [False]

        def create():
            def action():
                invasserted[0] = True
                return invasserted[0]
            return xs.finally_action(action)

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'C' and results[0].time == 250)
        assert(invasserted[0])

    def test_finally_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
        invasserted = [False]

        def create():
            def action():
                invasserted[0] = True
                return invasserted[0]

            return xs.finally_action(action)

        results = scheduler.start(create).messages
        self.assertEqual(2, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'C' and results[1].time == 250)
        assert(invasserted[0])

    def test_finally_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
        invasserted = [False]

        def create():
            def action():
                invasserted[0] = True
                return invasserted[0]

            return xs.finally_action(action)

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'E' and results[0].time == 250 and results[0].value.exception == ex)
        assert(invasserted[0])
