import unittest

import reactivex
from reactivex import operators as ops
from reactivex.observable.observable import Observable
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.recorded import Recorded

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestZipLatest(unittest.TestCase):
    def test_zip_latest_never_never(self):
        scheduler = TestScheduler()
        o1 = reactivex.never()
        o2 = reactivex.never()

        def create():
            return o1.pipe(ops.zip_latest(o2))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_latest_never_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(210)]
        o1 = reactivex.never()
        o2 = scheduler.create_hot_observable(msgs)

        def create():
            return o1.pipe(ops.zip_latest(o2))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_latest_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_completed(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_latest_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_latest_non_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_latest_never_non_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = reactivex.never()

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_latest_non_empty_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = reactivex.never()

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_latest_non_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(220, (2, 3)), on_completed(230)]

    def test_zip_latest_empty_error(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_error_empty(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_never_error(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = reactivex.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_error_never(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = reactivex.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_error_error(self):
        ex1 = Exception("ex1")
        ex2 = Exception("ex2")
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex1)]
        msgs2 = [on_next(150, 1), on_error(220, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex2)]

    def test_zip_latest_some_error(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_error_some(self):
        ex = Exception("ex")
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip_latest(e1))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_latest_different_speeds(self):
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1),
            on_next(215, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(290, 5),
            on_completed(310),
        ]
        msgs2 = [
            on_next(150, "a"),
            on_next(210, "b"),
            on_next(250, "c"),
            on_next(270, "d"),
            on_next(280, "e"),
            on_completed(300),
        ]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert e1.subscriptions == [subscribe(200, 300)]
        assert results.messages == [
            on_next(215, (2, "b")),
            on_next(250, (4, "c")),
            on_next(290, (5, "e")),
            on_completed(300),
        ]

    def test_zip_latest_one_after_other(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_next(230, 3), on_completed(240)]
        msgs2 = [on_next(250, "a"), on_next(260, "b"), on_completed(270)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip_latest(e2))

        results = scheduler.start(create)
        assert e1.subscriptions == [subscribe(200, 240)]
        assert results.messages == [on_next(250, (3, "a")), on_completed(250)]

    def test_zip_latest_100_observables_with_linearly_increased_speeds(self):
        scheduler = TestScheduler()

        observables: list[Observable[int]] = []

        for i in range(1, 101):
            msgs: list[Recorded[int]] = []
            for j in range(0, 200, i):
                msgs.append(on_next(201 + j, i))

            msgs.append(on_completed(500))

            observables.append(scheduler.create_hot_observable(msgs))

        def create():
            return observables[0].pipe(ops.zip_latest(*observables[1:]))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(201, tuple(range(1, 101))),
            on_next(301, tuple(range(1, 101))),
            on_completed(500),
        ]

    def test_zip_latest_requires_a_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one source"):
            reactivex.zip_latest()

    def test_zip_latest_one_source(self) -> None:
        values: list[tuple[int, ...]] = []
        reactivex.of(1, 2).pipe(ops.zip_latest()).subscribe(values.append)
        assert values == [(1,), (2,)]

    def test_zip_latest_synchronous_sources_use_final_pending_value(self) -> None:
        values: list[tuple[object, ...]] = []
        completed: list[bool] = []
        reactivex.zip_latest(reactivex.of(1, 2), reactivex.of("a", "b")).subscribe(
            values.append, on_completed=lambda: completed.append(True)
        )
        assert values == [(2, "a")]
        assert completed == [True]

    def test_zip_latest_empty_source_skips_later_subscriptions(self) -> None:
        subscribed_to_second: list[bool] = []

        def second_subscribe(observer, scheduler=None):
            subscribed_to_second.append(True)
            return reactivex.empty().subscribe(observer, scheduler=scheduler)

        values: list[tuple[object, ...]] = []
        reactivex.zip_latest(
            reactivex.empty(), reactivex.create(second_subscribe)
        ).subscribe(values.append)
        assert values == []
        assert subscribed_to_second == []

    def test_zip_latest_none_is_a_value(self) -> None:
        scheduler = TestScheduler()
        first = scheduler.create_hot_observable(on_next(215, None), on_completed(230))
        second = scheduler.create_hot_observable(on_next(220, "a"), on_completed(240))
        result = scheduler.start(lambda: reactivex.zip_latest(first, second))
        assert result.messages == [on_next(220, (None, "a")), on_completed(230)]
