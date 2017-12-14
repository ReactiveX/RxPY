import unittest

from rx.core import Observer, Observable, Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject
from rx.operators.connectableobservable import ConnectableObservable

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class MySubject(Observable, Observer):

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


class TestConnectableObservable(unittest.TestCase):

    def test_connectable_observable_creation(self):
        y = [0]

        s2 = Subject()
        co2 = ConnectableObservable(Observable.return_value(1), s2)

        def send(x):
            y[0] = x
        co2.subscribe_callbacks(send=send)
        self.assertNotEqual(1, y[0])

        co2.connect()
        self.assertEqual(1, y[0])

    def test_connectable_observable_connected(self):
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
        disconnect = conn.connect(scheduler)

        res = scheduler.start(lambda: conn)

        assert res.messages == [
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            close(250)]

    def test_connectable_observable_not_connected(self):
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

        res = scheduler.start(lambda: conn)

        assert res.messages == []

    def test_connectable_observable_disconnected(self):
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
        disconnect = conn.connect(scheduler)
        disconnect.dispose()

        res = scheduler.start(lambda: conn)

        assert res.messages == []

    def test_connectable_observable_disconnect_future(self):
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
        subject.dispose_on(3, conn.connect())

        res = scheduler.start(lambda: conn)

        assert res.messages == [
            send(210, 1),
            send(220, 2),
            send(230, 3)]

    def test_connectable_observable_multiple_non_overlapped_connections(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(210, 1),
            send(220, 2),
            send(230, 3),
            send(240, 4),
            send(250, 5),
            send(260, 6),
            send(270, 7),
            send(280, 8),
            send(290, 9),
            close(300)
        )

        subject = Subject()

        conn = xs.multicast(subject)

        c1 = [None]
        def action10(scheduler, state):
            c1[0] = conn.connect(scheduler)
        scheduler.schedule_absolute(225, action10)

        def action11(scheduler, state):
            c1[0].dispose()
        scheduler.schedule_absolute(241, action11)

        def action12(scheduler, state):
            c1[0].dispose() # idempotency test
        scheduler.schedule_absolute(245, action12)

        def action13(scheduler, state):
            c1[0].dispose() # idempotency test
        scheduler.schedule_absolute(251, action13)

        def action14(scheduler, state):
            c1[0].dispose() # idempotency test
        scheduler.schedule_absolute(260, action14)

        c2 = [None]
        def action20(scheduler, state):
            c2[0] = conn.connect(scheduler)
        scheduler.schedule_absolute(249, action20)

        def action21(scheduler, state):
            c2[0].dispose()
        scheduler.schedule_absolute(255, action21)

        def action22(scheduler, state):
            c2[0].dispose() # idempotency test
        scheduler.schedule_absolute(265, action22)

        def action23(scheduler, state):
            c2[0].dispose() # idempotency test
        scheduler.schedule_absolute(280, action23)

        c3 = [None]
        def action30(scheduler, state):
            c3[0] = conn.connect(scheduler)
        scheduler.schedule_absolute(275, action30)

        def action31(scheduler, state):
            c3[0].dispose()
        scheduler.schedule_absolute(295, action31)

        res = scheduler.start(lambda: conn)

        assert res.messages == [
            send(230, 3),
            send(240, 4),
            send(250, 5),
            send(280, 8),
            send(290, 9)]

        assert xs.subscriptions == [
            subscribe(225, 241),
            subscribe(249, 255),
            subscribe(275, 295)]
