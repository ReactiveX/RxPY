import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

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

        Observable.of(1,2,3,4,5).subscribe(results.append)

        assert(str([1,2,3,4,5]) == str(results))

    def test_of_empty(self):
        results = []

        Observable.of().subscribe(results.append)

        assert(len(results) == 0)

    def teest_of_with_scheduler(self):
        scheduler = TestScheduler()

        def create():
            return Observable.of(1,2,3,4,5, scheduler=scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
          on_next(201, 1),
          on_next(202, 2),
          on_next(203, 3),
          on_next(204, 4),
          on_next(205, 5),
          on_completed(206)
        )

    def teest_of_with_scheduler_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.of(scheduler=scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            on_completed(201)
        )
