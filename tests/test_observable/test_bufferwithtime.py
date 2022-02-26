import unittest

from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBufferWithCount(unittest.TestCase):
    def test_buffer_with_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(281, 4),
            on_next(321, 5),
            on_next(351, 6),
            on_next(381, 7),
            on_next(421, 8),
            on_next(471, 9),
            on_completed(600))

        def create():
            return xs.pipe(
                ops.buffer_with_time(100, 70),
                ops.map(lambda x: ",".join([str(a) for a in x]))
            )

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, "2,3,4"),
            on_next(370, "4,5,6"),
            on_next(440, "6,7,8"),
            on_next(510, "8,9"),
            on_next(580, ""),
            on_next(600, ""),
            on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_buffer_with_time_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(380, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_error(600, ex))

        def create():
            return xs.pipe(
                ops.buffer_with_time(100, 70),
                ops.map(lambda x: ",".join([str(a) for a in x]))
            )

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, "2,3,4"),
            on_next(370, "4,5,6"),
            on_next(440, "6,7,8"),
            on_next(510, "8,9"),
            on_next(580, ""),
            on_error(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_buffer_with_time_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(281, 4),
            on_next(321, 5),
            on_next(351, 6),
            on_next(381, 7),
            on_next(421, 8),
            on_next(471, 9),
            on_completed(600))

        def create():
            return xs.pipe(
                ops.buffer_with_time(100, 70),
                ops.map(lambda x: ",".join([str(a) for a in x]))
            )

        results = scheduler.start(create, disposed=370)
        assert results.messages == [on_next(300, "2,3,4")]
        assert xs.subscriptions == [subscribe(200, 370)]

    def test_buffer_with_time_basic_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(380, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_completed(600))

        def create():
            return xs.pipe(
                ops.buffer_with_time(100),
                ops.map(lambda x: ",".join([str(a) for a in x]))
            )

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, "2,3,4"),
            on_next(400, "5,6,7"),
            on_next(500, "8,9"),
            on_next(600, ""),
            on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
