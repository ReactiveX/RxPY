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


class TestPluck(unittest.TestCase):
    def test_pluck_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, {"prop": 1}),
            on_next(210, {"prop": 2}),
            on_next(240, {"prop": 3}),
            on_next(290, {"prop": 4}),
            on_next(350, {"prop": 5}),
            on_completed(400),
            on_next(410, {"prop": -1}),
            on_completed(420),
            on_error(430, Exception("ex")),
        )
        results = scheduler.start(create=lambda: xs.pipe(ops.pluck("prop")))

        assert results.messages == [
            on_next(210, 2),
            on_next(240, 3),
            on_next(290, 4),
            on_next(350, 5),
            on_completed(400),
        ]
        assert xs.subscriptions == [subscribe(200, 400)]


class TestPluckAttr(unittest.TestCase):
    def test_pluck_attr_completed(self):
        scheduler = TestScheduler()

        class DummyClass:
            def __init__(self, prop):
                self.prop = prop

        xs = scheduler.create_hot_observable(
            on_next(180, DummyClass(1)),
            on_next(210, DummyClass(2)),
            on_next(240, DummyClass(3)),
            on_next(290, DummyClass(4)),
            on_next(350, DummyClass(5)),
            on_completed(400),
            on_next(410, DummyClass(-1)),
            on_completed(420),
            on_error(430, Exception("ex")),
        )
        results = scheduler.start(create=lambda: xs.pipe(ops.pluck_attr("prop")))

        assert results.messages == [
            on_next(210, 2),
            on_next(240, 3),
            on_next(290, 4),
            on_next(350, 5),
            on_completed(400),
        ]
        assert xs.subscriptions == [subscribe(200, 400)]
