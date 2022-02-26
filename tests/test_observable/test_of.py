import unittest

import rx
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestOf(unittest.TestCase):
    def test_of(self):
        results = []

        rx.of(1, 2, 3, 4, 5).subscribe(results.append)

        assert str([1, 2, 3, 4, 5]) == str(results)

    def test_of_empty(self):
        results = []

        rx.of().subscribe(results.append)

        assert len(results) == 0

    def teest_of_with_scheduler(self):
        scheduler = TestScheduler()

        def create():
            return rx.of(1, 2, 3, 4, 5)

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(201, 1),
            on_next(202, 2),
            on_next(203, 3),
            on_next(204, 4),
            on_next(205, 5),
            on_completed(206),
        ]

    def teest_of_with_scheduler_empty(self):
        scheduler = TestScheduler()

        def create():
            return rx.of(scheduler=scheduler)

        results = scheduler.start(create=create)

        assert results.messages == [on_completed(201)]
