import unittest
from typing import Any, NoReturn

import reactivex
from reactivex import Observable, abc
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.coldobservable import ColdObservable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestDefer(unittest.TestCase):
    def test_defer_complete(self):
        xs: list[ColdObservable[int] | None] = [None]
        invoked = [0]
        scheduler = TestScheduler()

        def create() -> reactivex.Observable[Any]:
            def defer(_scheduler: abc.SchedulerBase) -> Observable[int]:
                invoked[0] += 1
                obs = scheduler.create_cold_observable(
                    on_next(100, scheduler.clock), on_completed(200)
                )
                xs[0] = obs
                return obs

            return reactivex.defer(defer)

        results = scheduler.start(create)
        assert results.messages == [on_next(300, 200), on_completed(400)]
        assert 1 == invoked[0]
        assert xs[0] is not None
        assert xs[0].subscriptions == [subscribe(200, 400)]

    def test_defer_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs: list[ColdObservable[int] | None] = [None]
        ex = "ex"

        def create() -> reactivex.Observable[Any]:
            def defer(_scheduler: abc.SchedulerBase) -> Observable[int]:
                invoked[0] += 1
                obs = scheduler.create_cold_observable(
                    on_next(100, scheduler.clock), on_error(200, ex)
                )
                xs[0] = obs
                return obs

            return reactivex.defer(defer)

        results = scheduler.start(create)

        assert results.messages == [on_next(300, 200), on_error(400, ex)]
        assert 1 == invoked[0]
        assert xs[0] is not None
        assert xs[0].subscriptions == [subscribe(200, 400)]

    def test_defer_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs: list[ColdObservable[int] | None] = [None]

        def create() -> reactivex.Observable[Any]:
            def defer(_scheduler: abc.SchedulerBase) -> Observable[int]:
                invoked[0] += 1
                obs = scheduler.create_cold_observable(
                    on_next(100, scheduler.clock),
                    on_next(200, invoked[0]),
                    on_next(1100, 1000),
                )
                xs[0] = obs
                return obs

            return reactivex.defer(defer)

        results = scheduler.start(create)
        assert results.messages == [on_next(300, 200), on_next(400, 1)]
        assert 1 == invoked[0]
        assert xs[0] is not None
        assert xs[0].subscriptions == [subscribe(200, 1000)]

    def test_defer_on_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = "ex"

        def create() -> reactivex.Observable[Any]:
            def defer(_scheduler: abc.SchedulerBase) -> NoReturn:
                invoked[0] += 1
                raise Exception(ex)

            return reactivex.defer(defer)

        results = scheduler.start(create)

        assert results.messages == [on_error(200, ex)]
        assert 1 == invoked[0]
