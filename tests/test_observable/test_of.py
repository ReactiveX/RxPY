import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestOf(unittest.TestCase):
    def test_of(self):
        results = []

        Observable.of(1,2,3,4,5).subscribe_callbacks(results.append)

        assert(str([1,2,3,4,5]) == str(results))

    def test_of_empty(self):
        results = []

        Observable.of().subscribe_callbacks(results.append)

        assert(len(results) == 0)

    def teest_of_with_scheduler(self):
        scheduler = TestScheduler()

        def create():
            return Observable.of(1,2,3,4,5)

        results = scheduler.start(create=create)

        assert results.messages == [
          send(201, 1),
          send(202, 2),
          send(203, 3),
          send(204, 4),
          send(205, 5),
          close(206)]

    def teest_of_with_scheduler_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.of(scheduler=scheduler)

        results = scheduler.start(create=create)

        assert results.messages == [
            close(201)]
