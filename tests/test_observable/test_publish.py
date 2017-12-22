import unittest

from rx.core import Observer, ObservableBase, Observable
from rx.operators.connectableobservable import ConnectableObservable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class MySubject(ObservableBase, Observer):

    def __init__(self):
        super(MySubject, self).__init__()

        self.dispose_on_map = {}
        self.subscribe_count = 0
        self.disposed = False

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

    def send(self, value):
        self.observer.send(value)
        if value in self.dispose_on_map:
            self.dispose_on_map[value].dispose()

    def throw(self, exception):
        self.observer.throw(exception)

    def close(self):
        self.observer.close()


class TestPublish(unittest.TestCase):

    def test_publish_cold_zip(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(40, 0),
            send(90, 1),
            send(150, 2),
            send(210, 3),
            send(240, 4),
            send(270, 5),
            send(330, 6),
            send(340, 7),
            close(390)
        )

        def create():
            def selector(ys):
                def result_selector(a, b):
                    return a + b
                return ys.zip(ys, result_selector=result_selector)

            return xs.publish(selector=selector)
        results = scheduler.start(create)

        assert results.messages == [send(210, 6),
            send(240, 8),
            send(270, 10),
            send(330, 12),
            send(340, 14), close(390)]
        assert xs.subscriptions == [subscribe(200, 390)]

    def test_ref_count_connects_on_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            close(250)
        )
        subject = MySubject()
        conn = ConnectableObservable(xs, subject)

        def create():
            return conn.ref_count()

        res = scheduler.start(create)

        assert res.messages == [
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            close(250)]
        assert(subject.disposed)

    def test_ref_count_notconnected(self):
        disconnected = [False]
        count = [0]

        def factory(scheduler):
            count[0] += 1

            def create(obs):
                def func():
                    disconnected[0] = True
                return func

            return Observable.create(create)

        xs = Observable.defer(factory)

        subject = MySubject()
        conn = ConnectableObservable(xs, subject)
        refd = conn.ref_count()
        dis1 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(1, subject.subscribe_count)
        assert(not disconnected[0])
        dis2 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(2, subject.subscribe_count)
        assert(not disconnected[0])
        dis1.dispose()
        assert(not disconnected[0])
        dis2.dispose()
        assert(disconnected[0])
        disconnected[0] = False
        dis3 = refd.subscribe()
        self.assertEqual(2, count[0])
        self.assertEqual(3, subject.subscribe_count)
        assert(not disconnected[0])
        dis3.dispose()
        assert(disconnected[0])

    def test_publish_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600)
        )
        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish()
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
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 550), subscribe(650, 800)]

    def test_publish_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            throw(600, ex))

        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish()
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
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11),
            send(560, 20),
            throw(600, ex)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish()
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
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11),
            send(560, 20),
            close(600)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish()
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
        assert results.messages == [send(340, 8)]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800)]

    def test_publish_multipleconnections(self):
        xs = Observable.never()
        ys = xs.publish()
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert(connection1 == connection2)
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert(connection1 != connection3)
        connection3.dispose()

    def test_publish_lambda_zip_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), result_selector=lambda prev, cur: cur + prev)

            return xs.publish(selector)
        results = scheduler.start(create)

        assert results.messages == [
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11),
            send(520, 20),
            send(560, 31),
            close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_lambda_zip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            throw(600, ex))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), result_selector=lambda prev, cur: cur + prev)
            return xs.publish(selector)
        results = scheduler.start(create)

        assert results.messages == [
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11),
            send(520, 20),
            send(560, 31),
            throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_lambda_zip_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), result_selector=lambda prev, cur: cur + prev)
            return xs.publish(selector)

        results = scheduler.start(create, disposed=470)
        assert results.messages == [
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11)]
        assert xs.subscriptions == [subscribe(200, 470)]
