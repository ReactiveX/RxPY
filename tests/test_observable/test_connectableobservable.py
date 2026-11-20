import unittest
from typing import Any, Generic, TypeVar

import reactivex
from reactivex import ConnectableObservable, Observable, abc
from reactivex import operators as ops
from reactivex.abc import DisposableBase, ObserverBase, SchedulerBase, SubjectBase
from reactivex.disposable import Disposable
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

_T = TypeVar("_T")

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class MySubject(Observable[_T], SubjectBase[_T], Generic[_T]):
    def __init__(self) -> None:
        super().__init__()

        self.dispose_on_map: dict[_T, DisposableBase] = {}
        self.subscribe_count = 0
        self.disposed = False
        self.observer: ObserverBase[_T]

    def _subscribe_core(
        self,
        observer: ObserverBase[_T],
        scheduler: SchedulerBase | None = None,
    ) -> DisposableBase:
        self.subscribe_count += 1
        self.observer = observer

        class Duck(DisposableBase):
            def __init__(self, this: MySubject[_T]) -> None:
                self.this = this

            def dispose(self) -> None:
                self.this.disposed = True

        return Duck(self)

    def dispose_on(self, value: _T, disposable: DisposableBase) -> None:
        self.dispose_on_map[value] = disposable

    def on_next(self, value: _T) -> None:
        self.observer.on_next(value)
        if value in self.dispose_on_map:
            self.dispose_on_map[value].dispose()

    def on_error(self, error: Exception) -> None:
        self.observer.on_error(error)

    def on_completed(self) -> None:
        self.observer.on_completed()


class TestConnectableObservable(unittest.TestCase):
    def test_connectable_observable_creation(self):
        y = [0]

        s2: Subject[int] = Subject()
        co2 = ConnectableObservable(reactivex.return_value(1), s2)

        def on_next(x: int) -> None:
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
            on_completed(250),
        )

        subject: MySubject[int] = MySubject()

        conn = ConnectableObservable(xs, subject)
        conn.connect(scheduler)

        res = scheduler.start(lambda: conn)

        assert res.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        ]

    def test_connectable_observable_not_connected(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        )

        subject: MySubject[int] = MySubject()

        conn = ConnectableObservable(xs, subject)

        res = scheduler.start(lambda: conn)

        assert res.messages == []

    def test_connectable_observable_disconnected(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        )

        subject: MySubject[int] = MySubject()

        conn = ConnectableObservable(xs, subject)
        disconnect = conn.connect(scheduler)
        assert disconnect is not None
        disconnect.dispose()

        res = scheduler.start(lambda: conn)

        assert res.messages == []

    def test_connectable_observable_disconnect_future(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250),
        )

        subject: MySubject[int] = MySubject()

        conn = ConnectableObservable(xs, subject)
        connection = conn.connect()
        assert connection is not None
        subject.dispose_on(3, connection)

        res = scheduler.start(lambda: conn)

        assert res.messages == [on_next(210, 1), on_next(220, 2), on_next(230, 3)]

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
            on_completed(300),
        )

        subject: Subject[int] = Subject()

        conn = xs.pipe(ops.multicast(subject))

        c1: list[DisposableBase | None] = [None]

        def action10(scheduler: abc.SchedulerBase, state: Any) -> None:
            c1[0] = conn.connect(scheduler)

        scheduler.schedule_absolute(225, action10)

        def action11(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c1[0] is not None
            c1[0].dispose()

        scheduler.schedule_absolute(241, action11)

        def action12(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c1[0] is not None
            c1[0].dispose()  # idempotency test

        scheduler.schedule_absolute(245, action12)

        def action13(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c1[0] is not None
            c1[0].dispose()  # idempotency test

        scheduler.schedule_absolute(251, action13)

        def action14(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c1[0] is not None
            c1[0].dispose()  # idempotency test

        scheduler.schedule_absolute(260, action14)

        c2: list[DisposableBase | None] = [None]

        def action20(scheduler: abc.SchedulerBase, state: Any) -> None:
            c2[0] = conn.connect(scheduler)

        scheduler.schedule_absolute(249, action20)

        def action21(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c2[0] is not None
            c2[0].dispose()

        scheduler.schedule_absolute(255, action21)

        def action22(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c2[0] is not None
            c2[0].dispose()  # idempotency test

        scheduler.schedule_absolute(265, action22)

        def action23(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c2[0] is not None
            c2[0].dispose()  # idempotency test

        scheduler.schedule_absolute(280, action23)

        c3: list[DisposableBase | None] = [None]

        def action30(scheduler: abc.SchedulerBase, state: Any) -> None:
            c3[0] = conn.connect(scheduler)

        scheduler.schedule_absolute(275, action30)

        def action31(scheduler: abc.SchedulerBase, state: Any) -> None:
            assert c3[0] is not None
            c3[0].dispose()

        scheduler.schedule_absolute(295, action31)

        res = scheduler.start(lambda: conn)

        assert res.messages == [
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(280, 8),
            on_next(290, 9),
        ]

        assert xs.subscriptions == [
            subscribe(225, 241),
            subscribe(249, 255),
            subscribe(275, 295),
        ]

    def test_connectable_observable_forward_scheduler(self):
        scheduler = TestScheduler()
        subscribe_scheduler: Any = "unknown"

        def subscribe(
            observer: ObserverBase[int], scheduler: SchedulerBase | None = None
        ) -> DisposableBase:
            nonlocal subscribe_scheduler
            subscribe_scheduler = scheduler
            return Disposable()

        xs = reactivex.create(subscribe)
        subject: MySubject[int] = MySubject()

        conn = ConnectableObservable(xs, subject)
        conn.connect(scheduler)

        assert subscribe_scheduler is scheduler
