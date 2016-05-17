import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBuffer(unittest.TestCase):

    def test_buffer_boundaries_simple(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_next(400, True),
            on_next(500, True),
            on_completed(900)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)

        res.messages.assert_equal(
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_next(400, lambda b: b == [ ]),
            on_next(500, lambda b: b == [7, 8, 9]),
            on_next(590, lambda b: b == [10]),
            on_completed(590)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 590)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 590)
        )

    def test_buffer_boundaries_on_completedboundaries(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_completed(400)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)


        res.messages.assert_equal(
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_next(400, lambda b: b == []),
            on_completed(400)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )


    def test_buffer_boundaries_on_errorsource(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                on_next(90, 1),
                on_next(180, 2),
                on_next(250, 3),
                on_next(260, 4),
                on_next(310, 5),
                on_next(340, 6),
                on_next(380, 7),
                on_error(400, ex)
        )

        ys = scheduler.create_hot_observable(
                on_next(255, True),
                on_next(330, True),
                on_next(350, True),
                on_completed(500)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)

        res.messages.assert_equal(
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_error(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

    def test_buffer_boundaries_on_errorboundaries(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                on_next(90, 1),
                on_next(180, 2),
                on_next(250, 3),
                on_next(260, 4),
                on_next(310, 5),
                on_next(340, 6),
                on_next(410, 7),
                on_next(420, 8),
                on_next(470, 9),
                on_next(550, 10),
                on_completed(590)
        )

        ys = scheduler.create_hot_observable(
                on_next(255, True),
                on_next(330, True),
                on_next(350, True),
                on_error(400, ex)
        )

        def create():
            return xs.buffer(ys)
        res = scheduler.start(create=create)

        res.messages.assert_equal(
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_error(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )
