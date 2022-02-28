import unittest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler


class TestToArray(ReactiveTest, unittest.TestCase):
    def test_toiterable_completed(self):
        scheduler = TestScheduler()
        msgs = [
            self.on_next(110, 1),
            self.on_next(220, 2),
            self.on_next(330, 3),
            self.on_next(440, 4),
            self.on_next(550, 5),
            self.on_completed(660),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(
                ops.to_iterable(),
                ops.map(list),
            )

        results = scheduler.start(create=create).messages

        assert len(results) == 2
        assert results[0].time == 660
        assert results[0].value.kind == "N"
        assert results[0].value.value == [2, 3, 4, 5]
        assert self.on_completed(660).equals(results[1])
        assert xs.subscriptions == [self.subscribe(200, 660)]

    def test_toiterableerror(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs = [
            self.on_next(110, 1),
            self.on_next(220, 2),
            self.on_next(330, 3),
            self.on_next(440, 4),
            self.on_next(550, 5),
            self.on_error(660, ex),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.to_iterable())

        results = scheduler.start(create=create).messages
        assert results == [self.on_error(660, ex)]
        assert xs.subscriptions == [self.subscribe(200, 660)]

    def test_toiterabledisposed(self):
        scheduler = TestScheduler()
        msgs = [
            self.on_next(110, 1),
            self.on_next(220, 2),
            self.on_next(330, 3),
            self.on_next(440, 4),
            self.on_next(550, 5),
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.to_iterable())

        results = scheduler.start(create=create).messages
        assert results == []
        assert xs.subscriptions == [self.subscribe(200, 1000)]
