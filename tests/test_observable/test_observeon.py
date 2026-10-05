import unittest

import reactivex
from reactivex import abc
from reactivex import operators as ops
from reactivex.disposable import Disposable
from reactivex.scheduler import ImmediateScheduler
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestObserveOn(unittest.TestCase):
    def test_observe_on_normal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1), on_next(210, 2), on_completed(250)
        )

        def create():
            return xs.pipe(ops.observe_on(scheduler))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_observe_on_error(self):
        scheduler = TestScheduler()
        ex = "ex"

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_error(210, ex),
        )

        def create():
            return xs.pipe(ops.observe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_observe_on_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.observe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == [on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_observe_on_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))

        def create():
            return xs.pipe(ops.observe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_observe_on_forward_subscribe_scheduler(self):
        scheduler = ImmediateScheduler()
        expected_subscribe_scheduler = ImmediateScheduler()

        actual_subscribe_scheduler = None

        def subscribe(
            observer: abc.ObserverBase[int],
            scheduler: abc.SchedulerBase | None = None,
        ) -> abc.DisposableBase:
            nonlocal actual_subscribe_scheduler
            actual_subscribe_scheduler = scheduler
            observer.on_completed()
            return Disposable()

        xs = reactivex.create(subscribe)

        xs.pipe(ops.observe_on(scheduler)).subscribe(
            scheduler=expected_subscribe_scheduler
        )

        assert expected_subscribe_scheduler == actual_subscribe_scheduler

    def test_observe_on_observer_throws(self):
        scheduler = TestScheduler()
        ex = Exception("ex")
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )
        results = scheduler.create_observer()
        errors = []

        def on_next_throw(value):
            raise ex

        def action(scheduler, state):
            source = xs.pipe(ops.observe_on(scheduler))
            source.subscribe(on_next_throw, errors.append)
            source.subscribe(results)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action)
        scheduler.start()

        assert errors == [ex]
        assert results.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_completed(230),
        ]
        assert xs.subscriptions == [subscribe(200, 210), subscribe(200, 230)]

    def test_observe_on_observer_throws_without_on_error(self):
        scheduler = TestScheduler()
        ex = Exception("ex")
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2))

        def on_next_throw(value):
            raise ex

        def action(scheduler, state):
            xs.pipe(ops.observe_on(scheduler)).subscribe(on_next_throw)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action)

        with self.assertLogs("Rx", level="ERROR") as logs:
            scheduler.start()

        assert len(logs.records) == 1
        assert logs.records[0].exc_info is not None
        assert logs.records[0].exc_info[1] is ex
        assert xs.subscriptions == [subscribe(200, 210)]
