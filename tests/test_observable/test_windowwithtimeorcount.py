import time
import unittest
from datetime import timedelta

from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithTime(unittest.TestCase):
    def test_window_with_time_or_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(205, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(370, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_completed(600),
        )

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return f"{i} {x}"

                return w.pipe(ops.map(inner_proj))

            return xs.pipe(
                ops.window_with_time_or_count(70, 3),
                ops.map_indexed(projection),
                ops.merge_all(),
            )

        results = scheduler.start(create)
        assert results.messages == [
            on_next(205, "0 1"),
            on_next(210, "0 2"),
            on_next(240, "0 3"),
            on_next(280, "1 4"),
            on_next(320, "2 5"),
            on_next(350, "2 6"),
            on_next(370, "2 7"),
            on_next(420, "3 8"),
            on_next(470, "4 9"),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_window_with_time_or_count_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(205, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(370, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_error(600, ex),
        )

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return f"{i} {x}"

                return w.pipe(ops.map(inner_proj))

            return xs.pipe(
                ops.window_with_time_or_count(70, 3),
                ops.map_indexed(projection),
                ops.merge_all(),
            )

        results = scheduler.start(create)

        assert results.messages == [
            on_next(205, "0 1"),
            on_next(210, "0 2"),
            on_next(240, "0 3"),
            on_next(280, "1 4"),
            on_next(320, "2 5"),
            on_next(350, "2 6"),
            on_next(370, "2 7"),
            on_next(420, "3 8"),
            on_next(470, "4 9"),
            on_error(600, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_window_with_time_or_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(205, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(370, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_completed(600),
        )

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return f"{i} {x}"

                return w.pipe(ops.map(inner_proj))

            return xs.pipe(
                ops.window_with_time_or_count(70, 3),
                ops.map_indexed(projection),
                ops.merge_all(),
            )

        results = scheduler.start(create, disposed=370)
        assert results.messages == [
            on_next(205, "0 1"),
            on_next(210, "0 2"),
            on_next(240, "0 3"),
            on_next(280, "1 4"),
            on_next(320, "2 5"),
            on_next(350, "2 6"),
            on_next(370, "2 7"),
        ]
        assert xs.subscriptions == [subscribe(200, 370)]

    def test_window_with_time_or_count_no_loss_on_slow_consumer(self) -> None:
        """A window closed by the timer must not drop concurrent emissions.

        The timer fires on another thread, so without synchronization the
        source thread keeps pushing into the subject that the timer has
        already completed, and those items are silently lost. See #694.
        """
        source: Subject[int] = Subject()
        total = 0

        def record(value: int) -> None:
            nonlocal total
            total = value

        def slow(_: int) -> None:
            time.sleep(0.01)

        subscription = source.pipe(
            ops.window_with_time_or_count(timedelta(milliseconds=50), 1_000),
            ops.flat_map(lambda window: window.pipe(ops.count())),
            ops.do_action(slow),
            ops.scan(lambda acc, x: acc + x, 0),
        ).subscribe(record)

        count = 300
        for i in range(count):
            time.sleep(0.001)
            source.on_next(i)
        source.on_completed()
        time.sleep(0.1)
        subscription.dispose()

        assert total == count
