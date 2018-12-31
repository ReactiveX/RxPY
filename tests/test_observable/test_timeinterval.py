import unittest
from datetime import timedelta

from rx.chained import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TimeInterval(object):
    def __init__(self, value, interval):
        if isinstance(interval, timedelta):
            interval = int(interval.microseconds / 1000.0)

        self.value = value
        self.interval = interval

    def __str__(self):
        return "%s@%s" % (self.value, self.interval)

    def equals(self, other):
        return other.interval == self.interval and other.value == self.value


class TestTimeInterval(unittest.TestCase):

    def test_time_interval_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3),
                                             on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

        def create():
            def mapper(x):
                return TimeInterval(x.value, x.interval)
            return xs.time_interval().map(mapper)
        results = scheduler.start(create)
        assert results.messages == [on_next(210, TimeInterval(2, 10)), on_next(230, TimeInterval(3, 20)),
                                    on_next(260, TimeInterval(4, 30)), on_next(300, TimeInterval(5, 40)),
                                    on_next(350, TimeInterval(6, 50)), on_completed(400)]

    def test_time_interval_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty().time_interval()

        results = scheduler.start(create)
        assert results.messages == [on_completed(200)]

    def test_time_interval_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw(ex).time_interval()

        results = scheduler.start(create)
        assert results.messages == [on_error(200, ex)]

    def test_time_interval_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().time_interval()

        results = scheduler.start(create)
        assert results.messages == []

    def test_time_interval_default_scheduler(self):
        import datetime
        import time
        xs = Observable.of(1, 2).time_interval().pluck_attr('interval')
        l = []
        d = xs.subscribe_(l.append)
        time.sleep(0.1)
        self.assertEqual(len(l), 2)
        [self.assertIsInstance(el, datetime.timedelta) for el in l]
