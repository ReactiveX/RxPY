import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestReduce(unittest.TestCase):

    def test_reduce_with_seed_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(lambda acc, x: acc + x, 42))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 42), on_completed(250)]

    def test_reduce_with_seed_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x, seed=42))

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 42 + 24), on_completed(250)]

    def test_reduce_with_seed_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x, seed=42))

        res = scheduler.start(create=create).messages
        assert res == [on_error(210, ex)]

    def test_reduce_with_seed_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x, seed=42))

        res = scheduler.start(create=create).messages
        assert res == []

    def test_reduce_with_seed_range(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, 1),
            on_next(210, 0),
            on_next(220, 1),
            on_next(230, 2),
            on_next(240, 3),
            on_next(250, 4),
            on_completed(260)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x, seed=42))

        res = scheduler.start(create=create).messages
        assert res == [on_next(260, 10 + 42), on_completed(260)]

    def test_reduce_without_seed_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x))

        res = scheduler.start(create=create).messages
        assert len(res) == 1
        assert res[0].value.kind == 'E' and res[0].value.exception is not None
        assert res[0].time == 250

    def test_reduce_without_seed_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]

        def create():
            return xs.pipe(ops.reduce(accumulator=lambda acc, x: acc + x))

        xs = scheduler.create_hot_observable(msgs)
        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 24), on_completed(250)]

    def test_reduce_without_seed_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(lambda acc, x: acc + x))

        res = scheduler.start(create=create).messages
        assert res == [on_error(210, ex)]

    def test_reduce_without_seed_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(lambda acc, x: acc + x))

        res = scheduler.start(create=create).messages
        assert res == []

    def test_reduce_without_seed_range(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, 1),
            on_next(210, 0),
            on_next(220, 1),
            on_next(230, 2),
            on_next(240, 3),
            on_next(250, 4),
            on_completed(260)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(ops.reduce(lambda acc, x: acc + x))

        res = scheduler.start(create=create).messages
        assert res == [on_next(260, 10), on_completed(260)]

    def test_reduce_seed_none_does_not_crash(self):
        rx.empty().pipe(
            ops.reduce(lambda acc, v: v, seed=None)
        ).subscribe()

if __name__ == '__main__':
    unittest.main()
