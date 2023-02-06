import unittest

from reactivex import operators as _
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.subscription import Subscription

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAll(unittest.TestCase):
    def test_all_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, True), on_completed(250)]

    def test_all_no_emit(self):
        """Should emit true if no item is emitted"""
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(250))

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, True), on_completed(250)]

    def test_all_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, True), on_completed(250)]

    def test_all_return_not_match(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, -2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(210, False), on_completed(210)]

    def test_all_some_none_match(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, 1),
            on_next(210, -2),
            on_next(220, -3),
            on_next(230, -4),
            on_completed(250),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(210, False), on_completed(210)]

    def test_all_some_match(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, 1),
            on_next(210, -2),
            on_next(220, 3),
            on_next(230, -4),
            on_completed(250),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(210, False), on_completed(210)]
        assert xs.subscriptions == [Subscription(200, 210)]

    def test_all_some_all_match(self):
        """Should emit true and complete after the source completes if all
        items pass the predicate test
        """
        scheduler = TestScheduler()
        msgs = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_completed(250),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, True), on_completed(250)]

    def test_all_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == [on_error(210, ex)]

    def test_all_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.all(lambda x: x > 0))

        res = scheduler.start(create=create).messages
        assert res == []
        assert xs.subscriptions == [Subscription(200, 1000)]


if __name__ == "__main__":
    unittest.main()
