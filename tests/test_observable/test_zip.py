import unittest

import rx
from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestZip(unittest.TestCase):
    def test_zip_never_never(self):
        scheduler = TestScheduler()
        o1 = rx.never()
        o2 = rx.never()

        def create():
            return o1.pipe(ops.zip(o2))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_never_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(210)]
        o1 = rx.never()
        o2 = scheduler.create_hot_observable(msgs)

        def create():
            return o1.pipe(ops.zip(o2))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_completed(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_non_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_zip_never_non_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = rx.never()

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_non_empty_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = rx.never()

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_non_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_next(220, 2 + 3), on_completed(230)]

    def test_zip_non_empty_non_empty_sequential(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(210, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(240, 1), on_next(245, 3), on_completed(250)]
        e1 = scheduler.create_cold_observable(msgs1)
        e2 = scheduler.create_cold_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(200 + 240, 1 + 1),
            on_next(200 + 245, 2 + 3),
            on_completed(200 + 245),
        ]

    def test_zip_non_empty_partial_sequential(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(210, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(240, 1), on_completed(250)]
        e1 = scheduler.create_cold_observable(msgs1)
        e2 = scheduler.create_cold_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_next(200 + 240, 1 + 1), on_completed(200 + 250)]

    def test_zip_empty_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_error_empty(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_never_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = rx.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_error_never(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = rx.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_error_error(self):
        ex1 = "ex1"
        ex2 = "ex2"
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex1)]
        msgs2 = [on_next(150, 1), on_error(220, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex2)]

    def test_zip_some_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_error_some(self):
        ex = "ex"
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.pipe(ops.zip(e1), ops.map(sum))

        results = scheduler.start(create)
        assert results.messages == [on_error(220, ex)]

    def test_zip_some_data_asymmetric1(self):
        scheduler = TestScheduler()

        def msgs1_factory():
            results = []
            for i in range(5):
                results.append(on_next(205 + i * 5, i))
            return results

        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 8, i))
            return results

        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create).messages
        assert length == len(results)
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert (
                results[i].value.kind == "N"
                and results[i].time == time
                and results[i].value.value == _sum
            )

    def test_zip_some_data_asymmetric2(self):
        scheduler = TestScheduler()

        def msgs1_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 5, i))

            return results

        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(5):
                results.append(on_next(205 + i * 8, i))
            return results

        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create).messages
        assert length == len(results)
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert (
                results[i].value.kind == "N"
                and results[i].time == time
                and results[i].value.value == _sum
            )

    def test_zip_some_data_symmetric(self):
        scheduler = TestScheduler()

        def msgs1_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 5, i))
            return results

        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 8, i))
            return results

        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.zip(e2), ops.map(sum))

        results = scheduler.start(create).messages
        assert length == len(results)
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert (
                results[i].value.kind == "N"
                and results[i].time == time
                and results[i].value.value == _sum
            )

    def test_zip_with_iterable_never_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1))
        n2 = []

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == []
        assert n1.subscriptions == [subscribe(200, 1000)]

    def test_zip_with_iterable_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
        n2 = []

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_completed(210)]
        assert n1.subscriptions == [subscribe(200, 210)]

    def test_zip_with_iterable_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
        n2 = [2]

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_completed(210)]
        assert n1.subscriptions == [subscribe(200, 210)]

    def test_zip_with_iterable_non_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(
            on_next(150, 1), on_next(215, 2), on_completed(220)
        )
        n2 = []

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_completed(215)]
        assert n1.subscriptions == [subscribe(200, 215)]

    def test_zip_with_iterable_never_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1))
        n2 = [2]

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == []
        assert n1.subscriptions == [subscribe(200, 1000)]

    def test_zip_with_iterable_non_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(
            on_next(150, 1), on_next(215, 2), on_completed(230)
        )
        n2 = [3]

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_next(215, 2 + 3), on_completed(230)]
        assert n1.subscriptions == [subscribe(200, 230)]

    def test_zip_with_iterable_error_empty(self):
        ex = "ex"
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
        n2 = []

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_error(220, ex)]
        assert n1.subscriptions == [subscribe(200, 220)]

    def test_zip_with_iterable_error_some(self):
        ex = "ex"
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
        n2 = [2]

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [on_error(220, ex)]
        assert n1.subscriptions == [subscribe(200, 220)]

    def test_zip_with_iterable_some_data_both_sides(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
        )
        n2 = [5, 4, 3, 2]

        def create():
            return n1.pipe(ops.zip_with_iterable(n2), ops.map(sum))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(210, 7),
            on_next(220, 7),
            on_next(230, 7),
            on_next(240, 7),
        ]
        assert n1.subscriptions == [subscribe(200, 1000)]
