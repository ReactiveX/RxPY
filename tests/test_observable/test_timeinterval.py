import unittest
from datetime import timedelta

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TimeInterval(object):
    def __init__(self, value, interval):
        if isinstance(interval, timedelta):
            interval = int(interval.microseconds/1000.0)

        self.value = value
        self.interval = interval

    def __str__(self):
        return "%s@%s" % (self.value, self.interval)

    def equals(self, other):
        return other.interval == self.interval and other.value == self.value


class TestTimeInterval(unittest.TestCase):

    def test_time_interval_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400))

        def create():
            def selector(x):
                return TimeInterval(x.value, x.interval)
            return xs.time_interval().map(selector)
        results = scheduler.start(create)
        results.messages.assert_equal(send(210, TimeInterval(2, 10)), send(230, TimeInterval(3, 20)), send(260, TimeInterval(4, 30)), send(300, TimeInterval(5, 40)), send(350, TimeInterval(6, 50)), close(400))

    def test_time_interval_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty().time_interval()

        results = scheduler.start(create)
        results.messages.assert_equal(close(200))

    def test_time_interval_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw_exception(ex).time_interval()

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_time_interval_never(self):
        scheduler = TestScheduler()
        def create():
            return Observable.never().time_interval()

        results = scheduler.start(create)
        results.messages.assert_equal()


    def test_time_interval_default_scheduler(self):
        import datetime
        xs = Observable.from_((1,2)).time_interval().pluck_attr('interval')
        l = []
        d = xs.subscribe_callbacks(lambda x: l.append(x))
        self.assertEqual(len(l), 2)
        [self.assertIsInstance(el, datetime.timedelta) for el in l]

