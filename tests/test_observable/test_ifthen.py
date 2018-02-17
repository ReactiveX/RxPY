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


class TestIf_then(unittest.TestCase):
    def test_if_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))

        def create():
            return Observable.if_then(lambda: True, xs, ys)
        results = scheduler.start(create=create)

        assert results.messages == [on_next(210, 1), on_next(250, 2), on_completed(300)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == []

    def test_if_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))
        def create():
            return Observable.if_then(lambda: False, xs, ys)
        results = scheduler.start(create=create)

        assert results.messages == [on_next(310, 3), on_next(350, 4), on_completed(400)]
        assert xs.subscriptions == []
        assert ys.subscriptions == [subscribe(200, 400)]

    def test_if_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))

        def create():
            def condition():
                raise Exception(ex)
            return Observable.if_then(condition, xs, ys)
        results = scheduler.start(create=create)

        assert results.messages == [on_error(200, ex)]
        assert xs.subscriptions == []
        assert ys.subscriptions == []

    def test_if_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2))
        ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))

        def create():
            return Observable.if_then(lambda: True, xs, ys)
        results = scheduler.start(create=create)

        assert results.messages == [on_next(210, 1), on_next(250, 2)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert ys.subscriptions == []

    def test_if_default_completed(self):
        b = [False]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(220, 2), on_next(330, 3), on_completed(440))

        def action(scheduler, state):
            b[0] = True
        scheduler.schedule_absolute(150, action)

        def create():
            def condition():
                return b[0]
            return Observable.if_then(condition, xs)
        results = scheduler.start(create)

        assert results.messages == [on_next(220, 2), on_next(330, 3), on_completed(440)]
        assert xs.subscriptions == [subscribe(200, 440)]

    def test_if_default_error(self):
        ex = 'ex'
        b = [False]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(220, 2), on_next(330, 3), on_error(440, ex))

        def action(scheduler, state):
            b[0] = True
        scheduler.schedule_absolute(150, action)

        def create():
            def condition():
                return b[0]
            return Observable.if_then(condition, xs)
        results = scheduler.start(create)

        assert results.messages == [on_next(220, 2), on_next(330, 3), on_error(440, ex)]
        assert xs.subscriptions == [subscribe(200, 440)]


    def test_if_default_never(self):
        b = [False]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(220, 2), on_next(330, 3))

        def action(scheduler, state):
            b[0] = True
        scheduler.schedule_absolute(150, action)

        def create():
            def condition():
                return b[0]
            return Observable.if_then(condition, xs)
        results = scheduler.start(create)

        assert results.messages == [on_next(220, 2), on_next(330, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_if_default_other(self):
        b = [True]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(220, 2), on_next(330, 3), on_error(440, 'ex'))

        def action(scheduler, state):
            b[0] = False
        scheduler.schedule_absolute(150, action)

        def create():
            def condition():
                return b[0]
            return Observable.if_then(condition, xs)
        results = scheduler.start(create)

        assert results.messages == [on_completed(200)]
        assert xs.subscriptions == []
