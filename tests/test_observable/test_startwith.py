import unittest

from rx import operators as _
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestStartWith(unittest.TestCase):
    def test_start_with(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.pipe(_.start_with(1))
        results = scheduler.start(create)
        assert results.messages == [on_next(200, 1), on_next(220, 2), on_completed(250)]

    # def test_start_with_scheduler(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

    #     def create():
    #         return xs.pipe(_.start_with(scheduler)
    #     results = scheduler.start(create)
    #     assert results.messages == [on_next(220, 2), on_completed(250)]

    def test_start_with_scheduler_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.pipe(_.start_with(42))
        results = scheduler.start(create)
        assert results.messages == [on_next(200, 42), on_next(220, 2), on_completed(250)]

    def test_start_with_immediate_scheduler_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.pipe(_.start_with(42))
        results = scheduler.start(create)
        assert results.messages == [on_next(200, 42), on_next(220, 2), on_completed(250)]

    def test_start_with_scheduler_keyword_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))

        def create():
            return xs.pipe(_.start_with(42))
        results = scheduler.start(create)
        assert results.messages == [on_next(200, 42), on_next(220, 2), on_completed(250)]
