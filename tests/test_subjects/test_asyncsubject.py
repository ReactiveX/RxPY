from nose.tools import raises

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import AsyncSubject
from rx.internal.exceptions import DisposedException

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
    subject = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

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
        on_next(1020, 12)
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
        on_error(660, 'ex')
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
    results2.messages.assert_equal(on_next(630, 7), on_completed(630))
    results3.messages.assert_equal(on_next(900, 7), on_completed(900))

def test_error():
    subject = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

    ex = 'ex'
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
        on_error(660, 'ex2')
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
    results2.messages.assert_equal(on_error(630, ex))
    results3.messages.assert_equal(on_error(900, ex))


def test_canceled():
    subject = [None]
    subscription = [None]
    subscription1 = [None]
    subscription2 = [None]
    subscription3 = [None]

    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_completed(630),
        on_next(640, 9),
        on_completed(650),
        on_error(660, 'ex')
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
    results2.messages.assert_equal(on_completed(630))
    results3.messages.assert_equal(on_completed(900))

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
        subject[0].on_next(1)
    scheduler.schedule_absolute(150, action9)

    def action10(scheduler, state=None):
        subject[0].on_next(2)
    scheduler.schedule_absolute(250, action10)

    def action11(scheduler, state=None):
        subject[0].on_next(3)
    scheduler.schedule_absolute(350, action11)

    def action12(scheduler, state=None):
        subject[0].on_next(4)
    scheduler.schedule_absolute(450, action12)

    def action13(scheduler, state=None):
        subject[0].on_next(5)
    scheduler.schedule_absolute(550, action13)

    @raises(DisposedException)
    def action14(scheduler, state=None):
        subject[0].on_next(6)
    scheduler.schedule_absolute(650, action14)

    @raises(DisposedException)
    def action15(scheduler, state=None):
        subject[0].on_completed()
    scheduler.schedule_absolute(750, action15)

    @raises(DisposedException)
    def action16(scheduler, state=None):
        subject[0].on_error('ex')
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
