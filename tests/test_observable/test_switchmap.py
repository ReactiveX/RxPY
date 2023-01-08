import unittest

from reactivex import interval
from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.marbles import marbles_testing
from reactivex.testing.subscription import Subscription

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSwitchMap(unittest.TestCase):
    def test_switch_map(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(300, "a"),
            on_next(400, "b"),
            on_next(500, "c"),
        )

        def create_inner(x: str):
            def create_changing(j: int):
                return (j, x)

            return interval(20).pipe(ops.map(create_changing))

        def create():
            return xs.pipe(ops.switch_map(project=create_inner))

        results = scheduler.start(create, disposed=580)
        # (i, j, x): i is the index of the outer emit;
        # j is the value of the inner interval;
        # x is the value of the outer emission
        assert results.messages == [
            on_next(320, (0, "a")),
            on_next(340, (1, "a")),
            on_next(360, (2, "a")),
            on_next(380, (3, "a")),
            on_next(420, (0, "b")),
            on_next(440, (1, "b")),
            on_next(460, (2, "b")),
            on_next(480, (3, "b")),
            on_next(520, (0, "c")),
            on_next(540, (1, "c")),
            on_next(560, (2, "c")),
        ]
        assert xs.subscriptions == [Subscription(200, 580)]

    def test_switch_map_inner_throws(self):
        """Inner throwing causes outer to throw"""
        ex = "ex"
        scheduler = TestScheduler()
        sources = [
            scheduler.create_cold_observable(on_next(100, "a"), on_next(300, "aa")),
            scheduler.create_cold_observable(on_next(50, "b"), on_error(120, ex)),
            scheduler.create_cold_observable(
                on_next(50, "wont happen"), on_error(120, "no")
            ),
        ]
        xs = scheduler.create_hot_observable(
            on_next(
                250,
                0,
            ),
            on_next(400, 1),
            on_next(
                550,
                2,
            ),
        )

        def create_inner(x: int):
            return sources[x]

        def create():
            return xs.pipe(ops.switch_map(create_inner))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(350, "a"),
            on_next(450, "b"),
            on_error(520, ex),
        ]
        assert sources[0].subscriptions == [Subscription(250, 400)]
        assert sources[1].subscriptions == [Subscription(400, 520)]
        assert sources[2].subscriptions == []

    def test_switch_map_outer_throws(self):
        """Outer throwing unsubscribes from all"""
        ex = "ABC"
        scheduler = TestScheduler()
        sources = [
            scheduler.create_cold_observable(on_next(100, "a"), on_next(300, "aa")),
            scheduler.create_cold_observable(on_next(50, "b"), on_error(120, ex)),
            scheduler.create_cold_observable(
                on_next(50, "wont happen"), on_error(120, "no")
            ),
        ]
        xs = scheduler.create_hot_observable(
            on_next(
                250,
                0,
            ),
            on_next(400, 1),
            on_error(430, ex),
        )

        def create_inner(x: int):
            return sources[x]

        def create():
            return xs.pipe(ops.switch_map(create_inner))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(350, "a"),
            on_error(430, ex),
        ]
        assert sources[0].subscriptions == [Subscription(250, 400)]
        assert sources[1].subscriptions == [Subscription(400, 430)]
        assert sources[2].subscriptions == []

    def test_switch_map_no_inner(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(500))
        # Fake inner which should never be subscribed to
        sources = [scheduler.create_cold_observable(on_next(20, 2))]

        def create_inner(_x: int):
            return sources.pop(0)

        def create():
            return xs.pipe(ops.switch_map(create_inner))

        results = scheduler.start(create)
        assert results.messages == [on_completed(500)]
        assert xs.subscriptions == [Subscription(200, 500)]
        assert sources[0].subscriptions == []

    def test_switch_map_inner_completes(self):
        """Inner completions do not affect outer"""
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(300, "d"),
            on_next(330, "f"),
            on_completed(540),
        )

        def create_inner(x: str):
            """An observable which will complete after 40 ticks"""
            return interval(20).pipe(ops.map(lambda j: (j, x)), ops.take(2))

        def create():
            return xs.pipe(ops.switch_map(create_inner))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(320, (0, "d")),
            on_next(350, (0, "f")),
            on_next(
                370, (1, "f")
            ),  # here the current inner is unsubscribed but not the outer
            on_completed(540),  # only outer completion affects
        ]

    def test_switch_map_default_mapper(self):
        with marbles_testing(timespan=10) as (start, cold, hot, exp):
            xs = hot(
                "               ---a---b------c-----",
                {
                    "a": cold("    --1--2", None, None),
                    "b": cold("        --1-2-3-4-5|", None, None),
                    "c": cold("               --1--2", None, None),
                },
                None,
            )
            expected = exp("    -----1---1-2-3--1--2", None, None)
            result = start(xs.pipe(ops.switch_map()))
            assert result == expected
