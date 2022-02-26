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


class RxException(Exception):
    pass


class TestForkJoin(unittest.TestCase):
    def test_fork_join_never_never(self):
        scheduler = TestScheduler()
        e1 = rx.never()
        e2 = rx.never()

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == []

    def test_fork_join_never_empty(self):
        scheduler = TestScheduler()
        e1 = rx.never()
        e2 = rx.empty()

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_completed(200)]

    def test_fork_join_never_non_empty(self):
        scheduler = TestScheduler()
        e1 = rx.never()
        e2 = scheduler.create_hot_observable(
            [on_next(150, 1), on_next(230, 2), on_completed(300)]
        )

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == []

    def test_fork_join_empty_empty(self):
        scheduler = TestScheduler()
        e1 = rx.empty()
        e2 = rx.empty()

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_completed(200)]

    def test_fork_join_empty_non_empty(self):
        scheduler = TestScheduler()
        e1 = rx.empty()
        e2 = scheduler.create_hot_observable(
            [on_next(150, 1), on_next(230, 2), on_completed(300)]
        )

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_completed(200)]

    def test_fork_join_non_empty_non_empty_right_last(self):
        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]

        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_next(240, (2, 3)), on_completed(240)]

    def test_fork_join_non_empty_non_empty_left_last(self):
        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(300)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]

        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_next(300, (2, 3)), on_completed(300)]

    def test_fork_join_empty_error(self):
        ex = RxException()

        scheduler = TestScheduler()
        e1 = rx.empty()
        e2 = scheduler.create_hot_observable(
            [on_next(150, 1), on_next(230, 2), on_error(300, ex)]
        )

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_completed(200)]

    def test_fork_join_never_error(self):
        ex = RxException()

        scheduler = TestScheduler()
        e1 = rx.never()
        e2 = scheduler.create_hot_observable(
            [on_next(150, 1), on_next(230, 2), on_error(300, ex)]
        )

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_error(300, ex)]

    def test_fork_join_non_empty_error_left_last(self):
        ex = RxException()

        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(250, 2), on_completed(330)]
        msgs2 = [on_next(150, 1), on_next(230, 2), on_error(300, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_error(300, ex)]

    def test_fork_join_non_empty_error_right_last(self):
        ex = RxException()

        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(250, 2), on_completed(300)]
        msgs2 = [on_next(150, 1), on_next(230, 2), on_error(330, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_error(330, ex)]

    def test_fork_join_error_error_left_last(self):
        ex = RxException()

        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(250, 2), on_error(340, ex)]
        msgs2 = [on_next(150, 1), on_next(230, 2), on_error(330, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_error(330, ex)]

    def test_fork_join_error_error_right_last(self):
        ex = RxException()

        scheduler = TestScheduler()

        msgs1 = [on_next(150, 1), on_next(250, 2), on_error(340, ex)]
        msgs2 = [on_next(150, 1), on_next(230, 2), on_error(370, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        results = scheduler.start(lambda: rx.fork_join(e1, e2))
        assert results.messages == [on_error(340, ex)]

    def test_fork_join_many(self):
        scheduler = TestScheduler()

        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(300, 9),
            on_completed(500),
        ]
        msgs2 = [
            on_next(150, 1),
            on_next(205, 3),
            on_next(220, 7),
            on_next(400, 3),
            on_completed(900),
        ]
        msgs3 = [
            on_next(150, 1),
            on_next(250, 2),
            on_next(300, 3),
            on_next(400, 9),
            on_next(500, 2),
            on_completed(850),
        ]
        msgs4 = [
            on_next(150, 1),
            on_next(400, 2),
            on_next(550, 10),
            on_next(560, 11),
            on_next(600, 3),
            on_completed(605),
        ]
        msgs5 = [
            on_next(150, 1),
            on_next(201, 3),
            on_next(550, 10),
            on_next(560, 11),
            on_next(600, 3),
            on_next(900, 99),
            on_completed(905),
        ]

        xs = [
            scheduler.create_hot_observable(x)
            for x in [msgs1, msgs2, msgs3, msgs4, msgs5]
        ]
        results = scheduler.start(lambda: rx.fork_join(*xs))
        assert results.messages == [on_next(905, (9, 3, 2, 3, 99)), on_completed(905)]

    def test_fork_join_many_ops(self):
        scheduler = TestScheduler()

        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(300, 9),
            on_completed(500),
        ]
        msgs2 = [
            on_next(150, 1),
            on_next(205, 3),
            on_next(220, 7),
            on_next(400, 3),
            on_completed(900),
        ]
        msgs3 = [
            on_next(150, 1),
            on_next(250, 2),
            on_next(300, 3),
            on_next(400, 9),
            on_next(500, 2),
            on_completed(850),
        ]
        msgs4 = [
            on_next(150, 1),
            on_next(400, 2),
            on_next(550, 10),
            on_next(560, 11),
            on_next(600, 3),
            on_completed(605),
        ]
        msgs5 = [
            on_next(150, 1),
            on_next(201, 3),
            on_next(550, 10),
            on_next(560, 11),
            on_next(600, 3),
            on_next(900, 99),
            on_completed(905),
        ]

        xs = [scheduler.create_hot_observable(x) for x in [msgs2, msgs3, msgs4, msgs5]]

        def create():
            return scheduler.create_hot_observable(msgs1).pipe(ops.fork_join(*xs))

        results = scheduler.start(create)
        assert results.messages == [on_next(905, (9, 3, 2, 3, 99)), on_completed(905)]
