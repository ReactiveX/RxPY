import unittest
from typing import Any

from reactivex import operators as ops
from reactivex.notification import Notification
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def sequence_equal(arr1: list[Any], arr2: list[Any]) -> bool:
    if len(arr1) != len(arr2):
        return False

    for i in range(len(arr1)):
        if arr1[i] != arr2[i]:
            return False
    return True


class TestBufferWithCount(unittest.TestCase):
    def test_buffer_with_count_reentrant_value(self) -> None:
        for skip, expected in [
            (1, [[1, 2], [2, 99], [99, 3], [3]]),
            (2, [[1, 2], [99, 3]]),
            (3, [[1, 2], [3]]),
        ]:
            with self.subTest(skip=skip):
                source: Subject[int] = Subject()
                buffers: list[list[int]] = []

                def receive(buffer: list[int]) -> None:
                    buffers.append(buffer)
                    if len(buffers) == 1:
                        source.on_next(99)

                source.pipe(ops.buffer_with_count(2, skip)).subscribe(receive)
                source.on_next(1)
                source.on_next(2)
                source.on_next(3)
                source.on_completed()

                assert buffers == expected

    def test_buffer_with_count_reentrant_completion(self) -> None:
        source: Subject[int] = Subject()
        buffers: list[list[int]] = []
        completed: list[bool] = []

        def receive(buffer: list[int]) -> None:
            buffers.append(buffer)
            if len(buffers) == 1:
                source.on_next(3)
                source.on_completed()

        source.pipe(ops.buffer_with_count(2)).subscribe(
            receive, on_completed=lambda: completed.append(True)
        )
        source.on_next(1)
        source.on_next(2)

        assert buffers == [[1, 2], [3]]
        assert completed == [True]

    def test_buffer_with_count_basic(self):
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
            on_completed(600),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(3, 2), ops.map(lambda x: str(x)))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, str([2, 3, 4])),
            on_next(350, str([4, 5, 6])),
            on_next(420, str([6, 7, 8])),
            on_next(600, str([8, 9])),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_buffer_with_count_disposed(self):
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
            on_completed(600),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(3, 2), ops.map(lambda x: str(x)))

        results = scheduler.start(create, disposed=370)

        assert results.messages == [
            on_next(280, str([2, 3, 4])),
            on_next(350, str([4, 5, 6])),
        ]
        assert xs.subscriptions == [subscribe(200, 370)]

    def test_buffer_count_partial_window(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(5))

        results = scheduler.start(create).messages
        assert 2 == len(results)
        assert isinstance(results[0].value, Notification)
        assert isinstance(results[1].value, Notification)
        assert (
            sequence_equal(results[0].value.value, [2, 3, 4, 5])
            and results[0].time == 250
        )
        assert results[1].value.kind == "C" and results[1].time == 250

    def test_buffer_count_full_windows(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(2))

        results = scheduler.start(create).messages
        self.assertEqual(3, len(results))
        assert isinstance(results[0].value, Notification)
        assert isinstance(results[1].value, Notification)
        assert isinstance(results[2].value, Notification)
        assert sequence_equal(results[0].value.value, [2, 3]) and results[0].time == 220
        assert sequence_equal(results[1].value.value, [4, 5]) and results[1].time == 240
        assert results[2].value.kind == "C" and results[2].time == 250

    def test_buffer_count_full_and_partial_windows(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(3))

        results = scheduler.start(create).messages
        self.assertEqual(3, len(results))
        assert isinstance(results[0].value, Notification)
        assert isinstance(results[1].value, Notification)
        assert isinstance(results[2].value, Notification)
        assert (
            sequence_equal(results[0].value.value, [2, 3, 4]) and results[0].time == 230
        )
        assert sequence_equal(results[1].value.value, [5]) and results[1].time == 250
        assert results[2].value.kind == "C" and results[2].time == 250

    def test_buffer_count_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_error(250, "ex"),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(5))

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert isinstance(results[0].value, Notification)
        assert results[0].value.kind == "E" and results[0].time == 250

    def test_buffer_count_skip_less(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(3, 1))

        results = scheduler.start(create).messages
        self.assertEqual(5, len(results))
        assert isinstance(results[0].value, Notification)
        assert isinstance(results[1].value, Notification)
        assert isinstance(results[2].value, Notification)
        assert isinstance(results[3].value, Notification)
        assert isinstance(results[4].value, Notification)
        assert (
            sequence_equal(results[0].value.value, [2, 3, 4]) and results[0].time == 230
        )
        assert (
            sequence_equal(results[1].value.value, [3, 4, 5]) and results[1].time == 240
        )
        assert sequence_equal(results[2].value.value, [4, 5]) and results[2].time == 250
        assert sequence_equal(results[3].value.value, [5]) and results[3].time == 250
        assert results[4].value.kind == "C" and results[4].time == 250

    def test_buffer_count_skip_more(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.buffer_with_count(2, 3))

        results = scheduler.start(create).messages
        self.assertEqual(3, len(results))
        assert isinstance(results[0].value, Notification)
        assert isinstance(results[1].value, Notification)
        assert isinstance(results[2].value, Notification)
        assert sequence_equal(results[0].value.value, [2, 3]) and results[0].time == 220
        assert sequence_equal(results[1].value.value, [5]) and results[1].time == 250
        assert results[2].value.kind == "C" and results[2].time == 250
