import unittest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkip(unittest.TestCase):
    def test_skip_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        )

        def create():
            return xs.pipe(ops.skip(20))

        results = scheduler.start(create)

        assert results.messages == [on_completed(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_complete_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        )

        def create():
            return xs.pipe(ops.skip(17))

        results = scheduler.start(create)

        assert results.messages == [on_completed(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_complete_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        )

        def create():
            return xs.pipe(ops.skip(10))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        ]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_Complete_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        )

        def create():
            return xs.pipe(ops.skip(0))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_completed(690),
        ]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_error_after(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_error(690, ex),
        )

        def create():
            return xs.pipe(ops.skip(20))

        results = scheduler.start(create)

        assert results.messages == [on_error(690, ex)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_error_same(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_error(690, ex),
        )

        def create():
            return xs.pipe(ops.skip(17))

        results = scheduler.start(create)

        assert results.messages == [on_error(690, ex)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_error_before(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_error(690, ex),
        )

        def create():
            return xs.pipe(ops.skip(3))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
            on_error(690, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_skip_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
        )

        def create():
            return xs.pipe(ops.skip(3))

        results = scheduler.start(create, disposed=250)
        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_skip_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, 6),
            on_next(150, 4),
            on_next(210, 9),
            on_next(230, 13),
            on_next(270, 7),
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
            on_next(410, 15),
            on_next(415, 16),
            on_next(460, 72),
            on_next(510, 76),
            on_next(560, 32),
            on_next(570, -100),
            on_next(580, -3),
            on_next(590, 5),
            on_next(630, 10),
        )

        def create():
            return xs.pipe(ops.skip(3))

        results = scheduler.start(create, disposed=400)
        assert results.messages == [
            on_next(280, 1),
            on_next(300, -1),
            on_next(310, 3),
            on_next(340, 8),
            on_next(370, 11),
        ]
        assert xs.subscriptions == [subscribe(200, 400)]


if __name__ == "__main__":
    unittest.main()
