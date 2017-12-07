from nose.tools import raises

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import AsyncSubject
from rx.internal.exceptions import DisposedException

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
    subject = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

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
        subject[0] = AsyncSubject()
    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(subject[0])
    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()
    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = subject[0].subscribe(results1)
    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = subject[0].subscribe(results2)
    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = subject[0].subscribe(results3)
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
    results2.messages.assert_equal()
    results3.messages.assert_equal()


def test_finite():
    subject = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

    scheduler = TestScheduler()
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
        throw(660, 'ex')
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler, state=None):
        subject[0] = AsyncSubject()
    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(subject[0])
    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()
    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = subject[0].subscribe(results1)
    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = subject[0].subscribe(results2)
    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = subject[0].subscribe(results3)
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
    results2.messages.assert_equal(send(630, 7), close(630))
    results3.messages.assert_equal(send(900, 7), close(900))

def test_error():
    subject = [None]
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
        throw(660, 'ex2')
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action(scheduler, state=None):
        subject[0] = AsyncSubject()
    scheduler.schedule_absolute(100, action)

    def action1(scheduler, state=None):
        subscription[0] = xs.subscribe(subject[0])
    scheduler.schedule_absolute(200, action1)

    def action2(scheduler, state=None):
        subscription[0].dispose()
    scheduler.schedule_absolute(1000, action2)

    def action3(scheduler, state=None):
        subscription1[0] = subject[0].subscribe(results1)
    scheduler.schedule_absolute(300, action3)

    def action4(scheduler, state=None):
        subscription2[0] = subject[0].subscribe(results2)
    scheduler.schedule_absolute(400, action4)

    def action5(scheduler, state=None):
        subscription3[0] = subject[0].subscribe(results3)
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
    results1.messages.assert_equal()
    results2.messages.assert_equal(throw(630, ex))
    results3.messages.assert_equal(throw(900, ex))


def test_canceled():
    subject = [None]
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
        subject[0] = AsyncSubject()
    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription[0] = xs.subscribe(subject[0])
    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription[0].dispose()
    scheduler.schedule_absolute(1000, action3)

    def action4(scheduler, state=None):
        subscription1[0] = subject[0].subscribe(results1)
    scheduler.schedule_absolute(300, action4)

    def action5(scheduler, state=None):
        subscription2[0] = subject[0].subscribe(results2)
    scheduler.schedule_absolute(400, action5)

    def action6(scheduler, state=None):
        subscription3[0] = subject[0].subscribe(results3)
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

def test_subject_disposed():
    subject = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]
    scheduler = TestScheduler()

    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()

    def action1(scheduler, state=None):
        subject[0] = AsyncSubject()
    scheduler.schedule_absolute(100, action1)

    def action2(scheduler, state=None):
        subscription1[0] = subject[0].subscribe(results1)
    scheduler.schedule_absolute(200, action2)

    def action3(scheduler, state=None):
        subscription2[0] = subject[0].subscribe(results2)
    scheduler.schedule_absolute(300, action3)

    def action4(scheduler, state=None):
        subscription3[0] = subject[0].subscribe(results3)
    scheduler.schedule_absolute(400, action4)

    def action5(scheduler, state=None):
        subscription1[0].dispose()
    scheduler.schedule_absolute(500, action5)

    def action6(scheduler, state=None):
        subject[0].dispose()
    scheduler.schedule_absolute(600, action6)

    def action7(scheduler, state=None):
        subscription2[0].dispose()
    scheduler.schedule_absolute(700, action7)

    def action8(scheduler, state=None):
        subscription3[0].dispose()
    scheduler.schedule_absolute(800, action8)

    def action9(scheduler, state=None):
        subject[0].send(1)
    scheduler.schedule_absolute(150, action9)

    def action10(scheduler, state=None):
        subject[0].send(2)
    scheduler.schedule_absolute(250, action10)

    def action11(scheduler, state=None):
        subject[0].send(3)
    scheduler.schedule_absolute(350, action11)

    def action12(scheduler, state=None):
        subject[0].send(4)
    scheduler.schedule_absolute(450, action12)

    def action13(scheduler, state=None):
        subject[0].send(5)
    scheduler.schedule_absolute(550, action13)

    @raises(DisposedException)
    def action14(scheduler, state=None):
        subject[0].send(6)
    scheduler.schedule_absolute(650, action14)

    @raises(DisposedException)
    def action15(scheduler, state=None):
        subject[0].close()
    scheduler.schedule_absolute(750, action15)

    @raises(DisposedException)
    def action16(scheduler, state=None):
        subject[0].throw('ex')
    scheduler.schedule_absolute(850, action16)

    @raises(DisposedException)
    def action17(scheduler, state=None):
        subject[0].subscribe(None)
    scheduler.schedule_absolute(950, action17)

    scheduler.start()
    results1.messages.assert_equal()
    results2.messages.assert_equal()
    results3.messages.assert_equal()

if __name__ == '__main__':
    unittest.main()
