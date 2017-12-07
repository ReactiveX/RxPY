import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestPluck(unittest.TestCase):

    def test_pluck_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, {"prop": 1}),
            send(210, {"prop": 2}),
            send(240, {"prop": 3}),
            send(290, {"prop": 4}),
            send(350, {"prop": 5}),
            close(400),
            send(410, {"prop": -1}),
            close(420),
            throw(430, Exception('ex'))
        )
        results = scheduler.start(create=lambda: xs.pluck('prop'))

        results.messages.assert_equal(
            send(210, 2),
            send(240, 3),
            send(290, 4),
            send(350, 5),
            close(400)
        )
        xs.subscriptions.assert_equal(subscribe(200, 400))


class TestPluckAttr(unittest.TestCase):

    def test_pluck_attr_completed(self):
        scheduler = TestScheduler()

        class DummyClass:

            def __init__(self, prop):
                self.prop = prop

        xs = scheduler.create_hot_observable(
            send(180, DummyClass(1)),
            send(210, DummyClass(2)),
            send(240, DummyClass(3)),
            send(290, DummyClass(4)),
            send(350, DummyClass(5)),
            close(400),
            send(410, DummyClass(-1)),
            close(420),
            throw(430, Exception('ex'))
        )
        results = scheduler.start(create=lambda: xs.pluck_attr('prop'))

        results.messages.assert_equal(
            send(210, 2),
            send(240, 3),
            send(290, 4),
            send(350, 5),
            close(400)
        )
        xs.subscriptions.assert_equal(subscribe(200, 400))
