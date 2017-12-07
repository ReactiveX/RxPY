from rx.core import Observable, AnonymousObserver

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject

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

def test_infinite():
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    s = [None]
    scheduler = TestScheduler()

    xs = scheduler.create_hot_observable(
        send(70, 1),
        send(110, 2),
        send(220, 3),
        send(270, 4),
        send(340, 5),
        send(410, 6),
        send(520, 7),
        send(630, 8),
        send(710, 9),
        send(870, 10),
        send(940, 11),
        send(1020, 12)
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

    results1.messages.assert_equal(
        send(340, 5),
        send(410, 6),
        send(520, 7)
    )
    results2.messages.assert_equal(
        send(410, 6),
        send(520, 7),
        send(630, 8)
    )
    results3.messages.assert_equal(
        send(940, 11)
    )


def test_finite():
    scheduler = TestScheduler()
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    s = [None]

    xs = scheduler.create_hot_observable(
        send(70, 1),
        send(110, 2),
        send(220, 3),
        send(270, 4),
        send(340, 5),
        send(410, 6),
        send(520, 7),
        close(630),
        send(640, 9),
        close(650),
        throw(660, 'error')
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

    results1.messages.assert_equal(
        send(340, 5),
        send(410, 6),
        send(520, 7)
    )
    results2.messages.assert_equal(
        send(410, 6),
        send(520, 7),
        close(630)
    )
    results3.messages.assert_equal(
        close(900)
    )


def test_error():
    s = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    ex = 'ex'

    scheduler = TestScheduler()

    xs = scheduler.create_hot_observable(
        send(70, 1),
        send(110, 2),
        send(220, 3),
        send(270, 4),
        send(340, 5),
        send(410, 6),
        send(520, 7),
        throw(630, ex),
        send(640, 9),
        close(650),
        throw(660, 'foo')
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

    results1.messages.assert_equal(send(340, 5), send(410, 6), send(520, 7))
    results2.messages.assert_equal(send(410, 6), send(520, 7), throw(630, ex))
    results3.messages.assert_equal(throw(900, ex))


def test_canceled():
    s = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        close(630),
        send(640, 9),
        close(650),
        throw(660, 'ex')
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

    results1.messages.assert_equal()
    results2.messages.assert_equal(close(630))
    results3.messages.assert_equal(close(900))


def test_subject_create():
    _x = [None]
    _ex = [None]
    done = False

    def send(x):
        _x[0] = x

    def throw(ex):
        _ex[0] = ex

    def close():
        done = True

    v = AnonymousObserver(send, throw, close)

    o = Observable.return_value(42)

    s = Subject.create(v, o)

    def send2(x):
        _x[0] = x
    s.subscribe_callbacks(send2)

    assert(42 == _x[0])
    s.send(21)

    e = 'ex'
    s.throw(e)

    assert(e == _ex[0])

    s.close()
    assert(not done)
