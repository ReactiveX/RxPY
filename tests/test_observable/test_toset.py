import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToDict(unittest.TestCase):

    def test_to_set_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_completed(660)
        )

        def create():
            return xs.pipe(ops.to_set())

        results = scheduler.start(create)
        assert results.messages == [on_next(660, set([2, 3, 4, 5])), on_completed(660)]

        assert xs.subscriptions == [
            subscribe(200, 660)]

    def test_to_set_error(self):
        error = Exception()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_error(660, error)
        )

        results = scheduler.start(lambda: xs.pipe(ops.to_set()))

        assert results.messages == [
            on_error(660, error)]

        assert xs.subscriptions == [
            subscribe(200, 660)]

    def test_to_set_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5)
        )

        results = scheduler.start(lambda: xs.pipe(ops.to_set()))

        assert results.messages == []

        assert xs.subscriptions == [subscribe(200, 1000)]
