import unittest
from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class Timestamp(object):
    def __init__(self, value, timestamp):
        if isinstance(timestamp, datetime):
            timestamp = timestamp-datetime.utcfromtimestamp(0)
            timestamp = int(timestamp.microseconds/1000)

        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return "%s@%s" % (self.value, self.timestamp)

    def equals(self, other):
        return other.timestamp == self.timestamp and other.value == self.value


class TestTimeInterval(unittest.TestCase):

    def test_timestamp_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400))

        def create():
            def selector(x):
                return Timestamp(x.value, x.timestamp)
            return xs.timestamp(scheduler).map(selector)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, Timestamp(2, 210)), send(230, Timestamp(3, 230)), send(260, Timestamp(4, 260)), send(300, Timestamp(5, 300)), send(350, Timestamp(6, 350)), close(400))

    def test_timestamp_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty(scheduler).time_interval(scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(close(201))

    def test_timestamp_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw_exception(ex, scheduler).time_interval(scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(201, ex))

    def test_timestamp_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().time_interval(scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal()

