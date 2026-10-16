import unittest

import reactivex
from reactivex import operators as ops
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
def _raise(ex: Exception) -> None:
    raise RxException(ex)


class TestTimer(unittest.TestCase):
    def test_oneshot_timer_date_basic(self):
        scheduler = TestScheduler()
        date = scheduler.to_datetime(250.0)

        def create():
            return reactivex.timer(duetime=date)

        results = scheduler.start(create)
        assert results.messages == [on_next(250, 0), on_completed(250)]

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
        xs.subscribe(lambda x: _raise(Exception("ex")), scheduler=scheduler)

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
        xs.subscribe(lambda x: _raise(Exception("ex")), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = reactivex.timer(1, period=None)
        ys.subscribe(on_completed=lambda: _raise(Exception("ex")), scheduler=scheduler2)

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

    def test_periodic_timer_resubscription_respects_duetime(self):
        """Regression test for #697: timer with period should respect duetime on
        each resubscription (e.g. via repeat), not reuse stale absolute time."""
        scheduler = TestScheduler()
        source = reactivex.timer(10, 200, scheduler=scheduler)

        results = scheduler.start(
            lambda: source.pipe(
                ops.take(2),
                ops.repeat(),
            )
        )
        assert results.messages == [
            on_next(210, 0),
            on_next(410, 1),
            on_next(420, 0),
            on_next(620, 1),
            on_next(630, 0),
            on_next(830, 1),
            on_next(840, 0),
        ]
