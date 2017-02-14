import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestStopAndWait(unittest.TestCase):

    def test_never(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(150, 1)
        )

        def create():
            return xs.controlled(True, scheduler).stop_and_wait()

        results = scheduler.start(create)
        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_completed(250)
        )

        def create():
            return xs.controlled(True, scheduler).stop_and_wait()

        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))
