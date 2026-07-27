import unittest

import reactivex
from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestExclusive(unittest.TestCase):
    """Tests for the exclusive() operator.

    exclusive() subscribes to each inner observable emitted by the outer
    source, but only one at a time.  A new inner observable that arrives
    while another is still active is silently dropped.  When the current
    inner completes, the next inner observable to arrive is subscribed.
    """

    def test_exclusive_never(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.never().pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == []

    def test_exclusive_empty_outer(self):
        scheduler = TestScheduler()
        outer = scheduler.create_hot_observable(
            on_next(150, reactivex.empty()),
            on_completed(250),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == [on_completed(250)]

    def test_exclusive_single_inner_completes(self):
        scheduler = TestScheduler()
        inner = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_next(230, 2),
            on_completed(250),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner),
            on_next(205, inner),
            on_completed(300),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 1),
            on_next(230, 2),
            on_completed(300),
        ]

    def test_exclusive_drops_concurrent_inner(self):
        """A second inner observable arriving while the first is still active
        must be dropped (not subscribed to)."""
        scheduler = TestScheduler()
        inner1 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_next(230, 2),
            on_completed(260),
        )
        inner2 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(270, 3),
            on_completed(280),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner1),
            on_next(205, inner1),
            on_next(220, inner2),  # arrives while inner1 is active -> dropped
            on_completed(300),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        # Only inner1's items; inner2 is dropped entirely
        assert results.messages == [
            on_next(210, 1),
            on_next(230, 2),
            on_completed(300),
        ]

    def test_exclusive_sequential_inners(self):
        """A second inner observable that arrives *after* the first has
        completed must be subscribed to."""
        scheduler = TestScheduler()
        inner1 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_completed(250),
        )
        inner2 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(270, 2),
            on_completed(280),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner1),
            on_next(205, inner1),
            on_next(255, inner2),  # arrives after inner1 completed
            on_completed(300),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 1),
            on_next(270, 2),
            on_completed(300),
        ]

    def test_exclusive_multiple_concurrent_drops(self):
        """Multiple inner observables arriving while one is active are all
        dropped."""
        scheduler = TestScheduler()
        inner1 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_completed(300),
        )
        inner2 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(230, 2),
            on_completed(240),
        )
        inner3 = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(260, 3),
            on_completed(270),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner1),
            on_next(205, inner1),
            on_next(220, inner2),  # dropped
            on_next(250, inner3),  # dropped
            on_completed(350),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        # Only inner1's items; inner2 and inner3 are both dropped
        assert results.messages == [
            on_next(210, 1),
            on_completed(350),
        ]

    def test_exclusive_outer_error(self):
        error = Exception("outer error")
        scheduler = TestScheduler()
        inner = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_completed(400),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner),
            on_next(205, inner),
            on_error(250, error),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 1),
            on_error(250, error),
        ]

    def test_exclusive_inner_error(self):
        error = Exception("inner error")
        scheduler = TestScheduler()
        inner = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_error(230, error),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner),
            on_next(205, inner),
            on_completed(300),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 1),
            on_error(230, error),
        ]

    def test_exclusive_completes_when_outer_and_inner_done(self):
        """Completion should be deferred until both the outer and the active
        inner observable have finished."""
        scheduler = TestScheduler()
        inner = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(260, 1),
            on_completed(270),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner),
            on_next(205, inner),
            on_completed(240),  # outer completes before inner finishes
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create)
        # on_completed must arrive at 270 (when the inner finishes), not 240
        assert results.messages == [
            on_next(260, 1),
            on_completed(270),
        ]

    def test_exclusive_disposed(self):
        scheduler = TestScheduler()
        inner = scheduler.create_hot_observable(
            on_next(150, 0),
            on_next(210, 1),
            on_next(260, 2),
            on_completed(300),
        )
        outer = scheduler.create_hot_observable(
            on_next(150, inner),
            on_next(205, inner),
            on_completed(400),
        )

        def create():
            return outer.pipe(ops.exclusive())

        results = scheduler.start(create, disposed=250)
        # Subscription was disposed at 250, so only the first item is seen
        assert results.messages == [on_next(210, 1)]


if __name__ == "__main__":
    unittest.main()
