import unittest

from reactivex import operators, Observable
from reactivex.testing import ReactiveTest
from reactivex.testing.subscription import Subscription
from reactivex.testing.testscheduler import TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


class TestConcatMap(unittest.TestCase):
    def test_concat_map_and_flatten_each_item(self):
        scheduler = TestScheduler()
        e1 = scheduler.create_hot_observable(
            on_next(220, 1),
            on_next(300, 3),
            on_next(330, 5),
            on_completed(500),
        )
        e2 = scheduler.create_cold_observable(
            on_next(0, 10), on_next(10, 10), on_next(20, 10), on_completed(30)
        )

        def create_inner(x: int) -> Observable[int]:
            return e2.pipe(operators.map(lambda i: i * x))

        def test_create():
            return e1.pipe(operators.concat_map(create_inner))

        results = scheduler.start(test_create)
        assert results.messages == [
            on_next(220, 10),
            on_next(230, 10),
            on_next(240, 10),
            on_next(300, 30),
            on_next(310, 30),
            on_next(320, 30),
            on_next(330, 50),
            on_next(340, 50),
            on_next(350, 50),
            on_completed(500),
        ]
        assert e1.subscriptions == [Subscription(200, 500)]
        assert e2.subscriptions == [
            Subscription(220, 250),
            Subscription(300, 330),
            Subscription(330, 360),
        ]

    def test_concat_map_many_inner_inner_never_completes(self):
        """should concat_ap many outer to many inner, inner never completes"""
        scheduler = TestScheduler()
        e1 = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(300, 4),  # take 4 will never complete
            on_next(400, 5),
        )
        e2 = scheduler.create_cold_observable(
            on_next(0, 5), on_next(10, 55), on_next(20, 555)
        )

        def create_inner(x: int) -> Observable[int]:
            return e2.pipe(operators.take(x))

        def test_create():
            return e1.pipe(operators.concat_map(create_inner))

        results = scheduler.start(test_create)
        assert results.messages == [
            on_next(210, 5),
            on_next(300, 5),
            on_next(310, 55),
            on_next(320, 555),
        ]
        assert e1.subscriptions == [Subscription(200, 1000)]
        assert e2.subscriptions == [
            Subscription(210, 210),
            Subscription(300, 1000),  # unsubs when we dispose of e1 at end of test
        ]

    def test_concat_map_finalize_before_next(self):
        """should finalize before moving to the next observable"""
        scheduler = TestScheduler()
        e1 = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(220, 4),
            on_next(600, 6),
        )
        e2 = scheduler.create_cold_observable(
            on_next(50, 5), on_next(100, 55), on_completed(100)
        )

        def create_inner(x: int) -> Observable[int]:
            return e2.pipe(operators.map(lambda i: i * x))

        def test_create():
            return e1.pipe(operators.concat_map(create_inner))

        results = scheduler.start(test_create)
        assert results.messages == [
            on_next(260, 10),
            on_next(310, 110),
            on_next(310 + 50, 20),
            on_next(410, 220),
            on_next(650, 30),
            on_next(700, 330),
        ]
        assert e1.subscriptions == [Subscription(200, 1000)]
        assert e2.subscriptions == [
            Subscription(210, 310),
            Subscription(310, 410),
            Subscription(600, 700),
        ]

    def test_concat_map_inner_errors(self):
        """should propagate errors if the mapped inner throws"""
        scheduler = TestScheduler()
        e1 = scheduler.create_cold_observable(
            on_next(0, 0),
            on_next(50, 1),
            on_next(100, 2),
        )

        inners = [
            scheduler.create_cold_observable(
                on_next(10, 1), on_next(100, 2), on_completed(100)
            ),
            scheduler.create_cold_observable(
                on_next(10, 50), on_error(80, Exception("no"))
            ),
            scheduler.create_cold_observable(
                on_next(10, 1), on_next(100, 2), on_completed(100)
            ),
        ]

        def create_inner(x: int) -> Observable[int]:
            return inners[x]

        def test_create():
            return e1.pipe(operators.concat_map(create_inner))

        results = scheduler.start(test_create)
        assert results.messages == [
            on_next(210, 1),
            on_next(300, 2),
            on_next(310, 50),
            on_error(380, Exception("no")),
        ]
        assert e1.subscriptions == [Subscription(200, 380)]
        e2, e3, e4 = inners
        assert e2.subscriptions == [
            Subscription(200, 300),
        ]
        assert e3.subscriptions == [
            Subscription(300, 380),
        ]
        assert e4.subscriptions == []

    def test_concat_map_outer_errors(self):
        scheduler = TestScheduler()
        e1 = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(220, 4),
            on_error(230, Exception("a")),
        )
        e2 = scheduler.create_cold_observable(on_next(0, 5), on_completed(100))

        def create_inner(x: int) -> Observable[int]:
            return e2.pipe(operators.map(lambda i: i * x))

        def test_create():
            return e1.pipe(operators.concat_map(create_inner))

        results = scheduler.start(test_create)

        assert results.messages == [on_next(210, 10), on_error(230, Exception("a"))]
        assert e1.subscriptions == [Subscription(200, 230)]
        assert e2.subscriptions == [
            Subscription(210, 230)
        ]  # should not be any further sub and should unsub from e2 on outer error
