import unittest

from rx.core import Observer, Observable, ObservableBase
from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject
from rx.linq.connectableobservable import ConnectableObservable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class MySubject(ObservableBase, Observer):

    def __init__(self):

        super(MySubject, self).__init__()

        self.dispose_on_map = {}
        self.subscribe_count = 0
        self.disposed = False

    def _subscribe_core(self, observer):
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

    def on_error(self, exception):
        self.observer.on_error(exception)

    def on_completed(self):
        self.observer.on_completed()


class TestConnectableObservable(unittest.TestCase):

    def test_connectable_observable_creation(self):
        y = [0]

        s2 = Subject()
        co2 = ConnectableObservable(Observable.return_value(1), s2)

        def on_next(x):
            y[0] = x
        co2.subscribe(on_next=on_next)
        self.assertNotEqual(1, y[0])

        co2.connect()
        self.assertEqual(1, y[0])

    def test_connectable_observable_connected(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )

        subject = MySubject()

        conn = ConnectableObservable(xs, subject)
        disconnect = conn.connect()

        res = scheduler.start(lambda: conn)

        res.messages.assert_equal(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )

    def test_connectable_observable_not_connected(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )

        subject = MySubject()

        conn = ConnectableObservable(xs, subject)

        res = scheduler.start(lambda: conn)

        res.messages.assert_equal(
        )

    def test_connectable_observable_disconnected(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )

        subject = MySubject()

        conn = ConnectableObservable(xs, subject)
        disconnect = conn.connect()
        disconnect.dispose()

        res = scheduler.start(lambda: conn)

        res.messages.assert_equal(
        )

    def test_connectable_observable_disconnect_future(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )

        subject = MySubject()

        conn = ConnectableObservable(xs, subject)
        subject.dispose_on(3, conn.connect())

        res = scheduler.start(lambda: conn)

        res.messages.assert_equal(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3)
        )

    def test_connectable_observable_multiple_non_overlapped_connections(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_next(270, 7),
            on_next(280, 8),
            on_next(290, 9),
            on_completed(300)
        )

        subject = Subject()

        conn = xs.multicast(subject)

        c1 = [None]
        def action10(scheduler, state):
            c1[0] = conn.connect()
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
            c2[0] = conn.connect()
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
            c3[0] = conn.connect()
        scheduler.schedule_absolute(275, action30)

        def action31(scheduler, state):
            c3[0].dispose()
        scheduler.schedule_absolute(295, action31)

        res = scheduler.start(lambda: conn)

        res.messages.assert_equal(
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(280, 8),
            on_next(290, 9)
        )

        xs.subscriptions.assert_equal(
            subscribe(225, 241),
            subscribe(249, 255),
            subscribe(275, 295)
        )
