import unittest

from rx.core import Scheduler
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestStartWith(unittest.TestCase):
    def test_start_with(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

        def create():
            return xs.start_with(1)
        results = scheduler.start(create)
        assert results.messages == [send(200, 1), send(220, 2), close(250)]

    # def test_start_with_scheduler(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

    #     def create():
    #         return xs.start_with(scheduler)
    #     results = scheduler.start(create)
    #     assert results.messages == [send(220, 2), close(250)]

    def test_start_with_scheduler_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

        def create():
            return xs.start_with(42)
        results = scheduler.start(create)
        assert results.messages == [send(200, 42), send(220, 2), close(250)]

    def test_start_with_immediate_scheduler_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

        def create():
            return xs.start_with(42)
        results = scheduler.start(create)
        assert results.messages == [send(200, 42), send(220, 2), close(250)]

    def test_start_with_scheduler_keyword_and_arg(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

        def create():
            return xs.start_with(42)
        results = scheduler.start(create)
        assert results.messages == [send(200, 42), send(220, 2), close(250)]
