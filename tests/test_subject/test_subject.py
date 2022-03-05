from reactivex.subject import Subject
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


def test_infinite():
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    s = [None]
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

    def action1(scheduler, state=None):
        s[0] = Subject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(s[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = s[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = s[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = s[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler, state=None):
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler, state=None):
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()

    assert results1.messages == [on_next(340, 5), on_next(410, 6), on_next(520, 7)]
    assert results2.messages == [on_next(410, 6), on_next(520, 7), on_next(630, 8)]
    assert results3.messages == [on_next(940, 11)]


def test_finite():
    scheduler = TestScheduler()
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    s = [None]

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
        on_error(660, "error"),
    )

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler, state=None):
        s[0] = Subject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(s[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = s[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = s[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = s[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler, state=None):
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler, state=None):
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()

    assert results1.messages == [on_next(340, 5), on_next(410, 6), on_next(520, 7)]
    assert results2.messages == [on_next(410, 6), on_next(520, 7), on_completed(630)]
    assert results3.messages == [on_completed(900)]


def test_error():
    s = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
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
        on_error(660, "foo"),
    )

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action(scheduler, state=None):
        s[0] = Subject()

    scheduler.schedule_absolute(100, action)

    def action1(scheduler, state=None):
        subscription[0] = xs.subscribe(s[0])

    scheduler.schedule_absolute(200, action1)

    def action2(scheduler, state=None):
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action2)

    def action3(scheduler, state=None):
        subscription1[0] = s[0].subscribe(results1)

    scheduler.schedule_absolute(300, action3)

    def action4(scheduler, state=None):
        subscription2[0] = s[0].subscribe(results2)

    scheduler.schedule_absolute(400, action4)

    def action5(scheduler, state=None):
        subscription3[0] = s[0].subscribe(results3)

    scheduler.schedule_absolute(900, action5)

    def action6(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action6)

    def action7(scheduler, state=None):
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action7)

    def action8(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action8)

    def action9(scheduler, state=None):
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action9)

    scheduler.start()

    assert results1.messages == [on_next(340, 5), on_next(410, 6), on_next(520, 7)]
    assert results2.messages == [on_next(410, 6), on_next(520, 7), on_error(630, ex)]
    assert results3.messages == [on_error(900, ex)]


def test_canceled():
    s = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_completed(630), on_next(640, 9), on_completed(650), on_error(660, "ex")
    )

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler, state=None):
        s[0] = Subject()

    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(s[0])

    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()

    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = s[0].subscribe(results1)

    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = s[0].subscribe(results2)

    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = s[0].subscribe(results3)

    scheduler.schedule_absolute(900, action6)

    def action7(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(600, action7)

    def action8(scheduler, state=None):
        subscription2[0].dispose()

    scheduler.schedule_absolute(700, action8)

    def action9(scheduler, state=None):
        subscription1[0].dispose()

    scheduler.schedule_absolute(800, action9)

    def action10(scheduler, state=None):
        subscription3[0].dispose()

    scheduler.schedule_absolute(950, action10)

    scheduler.start()

    assert results1.messages == []
    assert results2.messages == [on_completed(630)]
    assert results3.messages == [on_completed(900)]
