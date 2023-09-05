import unittest

import reactivex
from reactivex import operators
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


class TestTimer(unittest.TestCase):
    def test_oneshot_timer_date_basic(self):
        scheduler = TestScheduler()
        date = scheduler.to_datetime(250.0)

        def create():
            return reactivex.timer(duetime=date)

        results = scheduler.start(create)
        assert results.messages == [on_next(250.0, 0), on_completed(250.0)]

    def test_oneshot_timer_date_passed(self):
        scheduler = TestScheduler()
        date = scheduler.to_datetime(90.0)

        def create():
            return reactivex.timer(date)

        results = scheduler.start(create)
        assert results.messages == [on_next(200, 0), on_completed(200)]

    def test_oneshot_timer_date_disposed(self):
        scheduler = TestScheduler()
        date = scheduler.to_datetime(1010.0)

        def create():
            return reactivex.timer(date)

        results = scheduler.start(create)
        assert results.messages == []

    def test_oneshot_timer_date_observer_throws(self):
        scheduler = TestScheduler()
        date = scheduler.to_datetime(250.0)
        xs = reactivex.timer(date)
        xs.subscribe(lambda x: _raise("ex"), scheduler=scheduler)

        self.assertRaises(RxException, scheduler.start)

    def test_oneshot_timer_timespan_basic(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(duetime=300)

        results = scheduler.start(create)
        assert results.messages == [on_next(500, 0), on_completed(500)]

    def test_oneshot_timer_timespan_zero(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(0)

        results = scheduler.start(create)
        assert results.messages == [on_next(200, 0), on_completed(200)]

    def test_oneshot_timer_timespan_negative(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(-1)

        results = scheduler.start(create)
        assert results.messages == [on_next(200, 0), on_completed(200)]

    def test_oneshot_timer_timespan_disposed(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(1000)

        results = scheduler.start(create)
        assert results.messages == []

    def test_oneshot_timer_timespan_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = reactivex.timer(11)
        xs.subscribe(lambda x: _raise("ex"), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = reactivex.timer(1, period=None)
        ys.subscribe(on_completed=lambda: _raise("ex"), scheduler=scheduler2)

        self.assertRaises(RxException, scheduler2.start)

    def test_periodic_timer_basic(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(duetime=300, period=400)

        results = scheduler.start(create)
        assert results.messages == [on_next(500, 0), on_next(900, 1)]

    def test_periodic_timer_equal_time_and_period(self):
        scheduler = TestScheduler()

        def create():
            return reactivex.timer(duetime=300, period=300)

        results = scheduler.start(create)
        assert results.messages == [on_next(500, 0), on_next(800, 1)]

    def test_periodic_timer_repeat(self):
        scheduler = TestScheduler()
        t = reactivex.timer(duetime=130, period=200, scheduler=scheduler)

        def create():
            return t.pipe(operators.take(3), operators.repeat())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(330, 0),
            on_next(530, 1),
            on_next(730, 2),
            on_next(860, 0),
        ]

    def test_periodic_timer_repeat_with_absolute_datetime(self):
        scheduler = TestScheduler()
        t = reactivex.timer(
            duetime=scheduler.to_datetime(360), period=200, scheduler=scheduler
        )  # here we have an absolute first value, so on second subscription, the timer should emit immediately

        def create():
            return t.pipe(operators.take(3), operators.repeat())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(360, 0),
            on_next(560, 1),
            on_next(760, 2),
            on_next(
                760, 0
            ),  # our duetime is absolute and in the past so new sub emits immediately
            on_next(960, 1),
        ]

    def test_periodic_timer_repeat_with_relative_timespan(self):
        scheduler = TestScheduler()
        t = reactivex.timer(
            duetime=scheduler.to_timedelta(130),
            period=scheduler.to_timedelta(250),
            scheduler=scheduler,
        )

        def create():
            return t.pipe(operators.take(3), operators.repeat())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(330, 0),
            on_next(580, 1),
            on_next(830, 2),
            on_next(960, 0),
        ]

    def test_periodic_timer_second_subscription(self):
        scheduler = TestScheduler()
        t = reactivex.timer(duetime=200, period=300, scheduler=scheduler)

        def create():
            return reactivex.merge(
                t.pipe(operators.map(lambda x: (x, "first"))),
                reactivex.concat(reactivex.timer(100, scheduler=scheduler), t).pipe(
                    operators.map(lambda x: (x, "second"))
                ),
            )

        results = scheduler.start(create)
        assert results.messages == [
            on_next(300, (0, "second")),
            on_next(400, (0, "first")),
            on_next(500, (0, "second")),
            on_next(700, (1, "first")),
            on_next(800, (1, "second")),
        ]

    def test_one_off_timer_repeat(self):
        scheduler = TestScheduler()
        t = reactivex.timer(duetime=230, scheduler=scheduler)

        def create():
            return t.pipe(operators.repeat())

        results = scheduler.start(create)
        assert results.messages == [
            on_next(430, 0),
            on_next(660, 0),
            on_next(890, 0),
        ]
