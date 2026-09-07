import pytest

from reactivex.abc import DisposableBase, SchedulerBase
from reactivex.internal.exceptions import DisposedException
from reactivex.subject import AsyncSubject
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


def test_infinite():
    subject: list[AsyncSubject[int] | None] = [None]
    subscription: list[DisposableBase | None] = [None]
    subscription1: list[DisposableBase | None] = [None]
    subscription2: list[DisposableBase | None] = [None]
    subscription3: list[DisposableBase | None] = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_next(630, 8),
        on_next(710, 9),
        on_next(870, 10),
        on_next(940, 11),
        on_next(1020, 12),
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler: SchedulerBase, state: object = None) -> None:
        subject[0] = AsyncSubject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription[0] = xs.subscribe(subject[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription[0] is not None
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription1[0] = subject[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription2[0] = subject[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription3[0] = subject[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription2[0] is not None
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription3[0] is not None
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()
    assert results1.messages == []
    assert results2.messages == []
    assert results3.messages == []


def test_finite():
    subject: list[AsyncSubject[int] | None] = [None]
    subscription: list[DisposableBase | None] = [None]
    subscription1: list[DisposableBase | None] = [None]
    subscription2: list[DisposableBase | None] = [None]
    subscription3: list[DisposableBase | None] = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_completed(630),
        on_next(640, 9),
        on_completed(650),
        on_error(660, "ex"),
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler: SchedulerBase, state: object = None) -> None:
        subject[0] = AsyncSubject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription[0] = xs.subscribe(subject[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription[0] is not None
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription1[0] = subject[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription2[0] = subject[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription3[0] = subject[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription2[0] is not None
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription3[0] is not None
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()
    assert results1.messages == []
    assert results2.messages == [on_next(630, 7), on_completed(630)]
    assert results3.messages == [on_next(900, 7), on_completed(900)]


def test_error():
    subject: list[AsyncSubject[int] | None] = [None]
    subscription: list[DisposableBase | None] = [None]
    subscription1: list[DisposableBase | None] = [None]
    subscription2: list[DisposableBase | None] = [None]
    subscription3: list[DisposableBase | None] = [None]

    ex = "ex"
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_error(630, ex),
        on_next(640, 9),
        on_completed(650),
        on_error(660, "ex2"),
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action(scheduler: SchedulerBase, state: object = None) -> None:
        subject[0] = AsyncSubject()

    scheduler.schedule_absolute(100, action)

    def action1(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription[0] = xs.subscribe(subject[0])

    scheduler.schedule_absolute(200, action1)

    def action2(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription[0] is not None
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action2)

    def action3(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription1[0] = subject[0].subscribe(results1)

    scheduler.schedule_absolute(300, action3)

    def action4(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription2[0] = subject[0].subscribe(results2)

    scheduler.schedule_absolute(400, action4)

    def action5(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription3[0] = subject[0].subscribe(results3)

    scheduler.schedule_absolute(900, action5)

    def action6(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action6)

    def action7(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription2[0] is not None
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action7)

    def action8(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action8)

    def action9(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription3[0] is not None
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action9)

    scheduler.start()
    assert results1.messages == []
    assert results2.messages == [on_error(630, ex)]
    assert results3.messages == [on_error(900, ex)]


def test_canceled():
    subject: list[AsyncSubject[int] | None] = [None]
    subscription: list[DisposableBase | None] = [None]
    subscription1: list[DisposableBase | None] = [None]
    subscription2: list[DisposableBase | None] = [None]
    subscription3: list[DisposableBase | None] = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_completed(630), on_next(640, 9), on_completed(650), on_error(660, "ex")
    )

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler: SchedulerBase, state: object = None) -> None:
        subject[0] = AsyncSubject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription[0] = xs.subscribe(subject[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription[0] is not None
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription1[0] = subject[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription2[0] = subject[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription3[0] = subject[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription2[0] is not None
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription3[0] is not None
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()
    assert results1.messages == []
    assert results2.messages == [on_completed(630)]
    assert results3.messages == [on_completed(900)]


def test_subject_disposed():
    subject: list[AsyncSubject[int] | None] = [None]
    subscription1: list[DisposableBase | None] = [None]
    subscription2: list[DisposableBase | None] = [None]
    subscription3: list[DisposableBase | None] = [None]
    scheduler = TestScheduler()

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler: SchedulerBase, state: object = None) -> None:
        subject[0] = AsyncSubject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription1[0] = subject[0].subscribe(results1)

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription2[0] = subject[0].subscribe(results2)

    scheduler.schedule_absolute(300, action3)

    def action4(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subscription3[0] = subject[0].subscribe(results3)

    scheduler.schedule_absolute(400, action4)

    def action5(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription1[0] is not None
        subscription1[0].dispose()

    scheduler.schedule_absolute(500, action5)

    def action6(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].dispose()

    scheduler.schedule_absolute(600, action6)

    def action7(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription2[0] is not None
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action7)

    def action8(scheduler: SchedulerBase, state: object = None) -> None:
        assert subscription3[0] is not None
        subscription3[0].dispose()

    scheduler.schedule_absolute(800, action8)

    def action9(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].on_next(1)

    scheduler.schedule_absolute(150, action9)

    def action10(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].on_next(2)

    scheduler.schedule_absolute(250, action10)

    def action11(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].on_next(3)

    scheduler.schedule_absolute(350, action11)

    def action12(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].on_next(4)

    scheduler.schedule_absolute(450, action12)

    def action13(scheduler: SchedulerBase, state: object = None) -> None:
        assert subject[0] is not None
        subject[0].on_next(5)

    scheduler.schedule_absolute(550, action13)

    def action14(scheduler: SchedulerBase, state: object = None) -> None:
        with pytest.raises(DisposedException):
            assert subject[0] is not None
            subject[0].on_next(6)

    scheduler.schedule_absolute(650, action14)

    def action15(scheduler: SchedulerBase, state: object = None) -> None:
        with pytest.raises(DisposedException):
            assert subject[0] is not None
            subject[0].on_completed()

    scheduler.schedule_absolute(750, action15)

    def action16(scheduler: SchedulerBase, state: object = None) -> None:
        with pytest.raises(DisposedException):
            assert subject[0] is not None
            subject[0].on_error(Exception("ex"))

    scheduler.schedule_absolute(850, action16)

    def action17(scheduler: SchedulerBase, state: object = None) -> None:
        with pytest.raises(DisposedException):
            assert subject[0] is not None
            subject[0].subscribe(None)

    scheduler.schedule_absolute(950, action17)

    scheduler.start()
    assert results1.messages == []
    assert results2.messages == []
    assert results3.messages == []
