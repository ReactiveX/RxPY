import unittest

import reactivex
from reactivex import ConnectableObservable, Observable
from reactivex import operators as ops
from reactivex.abc import ObserverBase
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class MySubject(Observable, ObserverBase):
    def __init__(self):
        super(MySubject, self).__init__()

        self.dispose_on_map = {}
        self.subscribe_count = 0
        self.disposed = False
        self.observer = None

    def _subscribe_core(self, observer, scheduler=None):
        self.subscribe_count += 1
        self.observer = observer

        class Duck:
            def __init__(self, this):
                self.this = this

            def dispose(self):
                self.this.disposed = True

        return Duck(self)

    def dispose_on(self, value, disposable):
        self.dispose_on_map[value] = disposable

    def on_next(self, value):
        self.observer.on_next(value)
        if value in self.dispose_on_map:
            self.dispose_on_map[value].dispose()

    def on_error(self, error):
        self.observer.on_error(error)

    def on_completed(self):
        self.observer.on_completed()


class TestPublish(unittest.TestCase):
    def test_publish_cold_zip(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(40, 0),
            on_next(90, 1),
            on_next(150, 2),
            on_next(210, 3),
            on_next(240, 4),
            on_next(270, 5),
            on_next(330, 6),
            on_next(340, 7),
            on_completed(390),
        )

        def create():
            def mapper(ys):
                return ys.pipe(
                    ops.zip(ys),
                    ops.map(sum),
                )

            return xs.pipe(ops.publish(mapper=mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(210, 6),
            on_next(240, 8),
            on_next(270, 10),
            on_next(330, 12),
            on_next(340, 14),
            on_completed(390),
        ]
        assert xs.subscriptions == [subscribe(200, 390)]

    def test_ref_count_connects_on_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        )
        subject = MySubject()
        conn = ConnectableObservable(xs, subject)

        def create():
            return conn.pipe(ops.ref_count())

        res = scheduler.start(create)

        assert res.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        ]
        assert subject.disposed

    def test_ref_count_notconnected(self):
        disconnected = [False]
        count = [0]

        def factory(scheduler):
            count[0] += 1

            def create(obs, scheduler=None):
                def func():
                    disconnected[0] = True

                return func

            return reactivex.create(create)

        xs = reactivex.defer(factory)

        subject = MySubject()
        conn = ConnectableObservable(xs, subject)
        refd = conn.pipe(ops.ref_count())
        dis1 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(1, subject.subscribe_count)
        assert not disconnected[0]
        dis2 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(2, subject.subscribe_count)
        assert not disconnected[0]
        dis1.dispose()
        assert not disconnected[0]
        dis2.dispose()
        assert disconnected[0]
        disconnected[0] = False
        dis3 = refd.subscribe()
        self.assertEqual(2, count[0])
        self.assertEqual(3, subject.subscribe_count)
        assert not disconnected[0]
        dis3.dispose()
        assert disconnected[0]

    def test_publish_basic(self):
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
        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish())

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

    def test_publish_error(self):
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

        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.publish())

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
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
            on_next(560, 20),
            on_error(600, ex),
        ]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_complete(self):
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
            ys[0] = xs.pipe(ops.publish())

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
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_dispose(self):
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
            ys[0] = xs.pipe(ops.publish())

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
        assert results.messages == [on_next(340, 8)]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800),
        ]

    def test_publish_multipleconnections(self):
        xs = reactivex.never()
        ys = xs.pipe(ops.publish())
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert connection1 == connection2
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert connection1 != connection3
        connection3.dispose()

    def test_publish_lambda_zip_complete(self):
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

            return xs.pipe(ops.publish(mapper))

        results = scheduler.start(create)

        assert results.messages == [
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

    def test_publish_lambda_zip_error(self):
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

            return xs.pipe(ops.publish(mapper))

        results = scheduler.start(create)

        assert results.messages == [
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

    def test_publish_lambda_zip_dispose(self):
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
                return _xs.pipe(ops.zip(_xs.pipe(ops.skip(1))), ops.map(sum))

            return xs.pipe(ops.publish(mapper))

        results = scheduler.start(create, disposed=470)
        assert results.messages == [
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
