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


class TestPublishValue(unittest.TestCase):
    def test_publishwithinitialvalue_basic(self):
        subscription = [None]
        connection = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        )
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish_value(1979))

        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            subscription[0].dispose()

        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        assert results.messages == [
            on_next(200, 1979),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
        ]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800),
        ]

    def test_publish_with_initial_value_error(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_error(600, ex),
        )
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish_value(1979))

        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            subscription[0].dispose()

        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        assert results.messages == [
            on_next(200, 1979),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
            on_next(560, 20),
            on_error(600, ex),
        ]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_with_initial_value_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        )
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish_value(1979))

        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            subscription[0].dispose()

        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        assert results.messages == [
            on_next(200, 1979),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_with_initial_value_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        )

        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish_value(1979))

        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            subscription[0].dispose()

        scheduler.schedule_absolute(350, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()

        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()

        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        assert results.messages == [on_next(200, 1979), on_next(340, 8)]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800),
        ]

    def test_publish_with_initial_value_multiple_connections(self):
        xs = reactivex.never()
        ys = xs.pipe(ops.publish_value(1979))
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert connection1 == connection2
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert connection1 != connection3

    def test_publish_with_initial_value_lambda_zip_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        )

        def create():
            def mapper(_xs):
                return _xs.pipe(
                    ops.zip(_xs.pipe(ops.skip(1))),
                    ops.map(sum),
                )

            return xs.pipe(ops.publish_value(1979, mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(220, 1982),
            on_next(280, 7),
            on_next(290, 5),
            on_next(340, 9),
            on_next(360, 13),
            on_next(370, 11),
            on_next(390, 13),
            on_next(410, 20),
            on_next(430, 15),
            on_next(450, 11),
            on_next(520, 20),
            on_next(560, 31),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_with_initial_value_lambda_zip_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_error(600, ex),
        )

        def create():
            def mapper(_xs):
                return _xs.pipe(
                    ops.zip(_xs.pipe(ops.skip(1))),
                    ops.map(sum),
                )

            return xs.pipe(ops.publish_value(1979, mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(220, 1982),
            on_next(280, 7),
            on_next(290, 5),
            on_next(340, 9),
            on_next(360, 13),
            on_next(370, 11),
            on_next(390, 13),
            on_next(410, 20),
            on_next(430, 15),
            on_next(450, 11),
            on_next(520, 20),
            on_next(560, 31),
            on_error(600, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_with_initial_value_lambda_zip_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        )

        def create():
            def mapper(_xs):
                return _xs.pipe(
                    ops.zip(_xs.pipe(ops.skip(1))),
                    ops.map(sum),
                )

            return xs.pipe(ops.publish_value(1979, mapper))

        results = scheduler.start(create, disposed=470)
        assert results.messages == [
            on_next(220, 1982),
            on_next(280, 7),
            on_next(290, 5),
            on_next(340, 9),
            on_next(360, 13),
            on_next(370, 11),
            on_next(390, 13),
            on_next(410, 20),
            on_next(430, 15),
            on_next(450, 11),
        ]
        assert xs.subscriptions == [subscribe(200, 470)]
