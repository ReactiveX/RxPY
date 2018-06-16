import unittest
from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class Timestamp(object):
    def __init__(self, value, timestamp):
        if isinstance(timestamp, datetime):
            timestamp = timestamp - datetime.utcfromtimestamp(0)
            timestamp = int(timestamp.microseconds / 1000)

        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return "%s@%s" % (self.value, self.timestamp)

    def equals(self, other):
        return other.timestamp == self.timestamp and other.value == self.value


class TestTimeInterval(unittest.TestCase):

    def test_timestamp_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

        def create():
            def mapper(x):
                return Timestamp(x.value, x.timestamp)
            return xs.timestamp().map(mapper)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, Timestamp(2, 210)), on_next(230, Timestamp(3, 230)),
                                    on_next(260, Timestamp(4, 260)), on_next(300, Timestamp(5, 300)),
                                    on_next(350, Timestamp(6, 350)), on_completed(400)]

    def test_timestamp_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty().time_interval()

        results = scheduler.start(create)
        assert results.messages == [on_completed(200)]

    def test_timestamp_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw(ex).time_interval()

        results = scheduler.start(create)
        assert results.messages == [on_error(200, ex)]

    def test_timestamp_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().time_interval()

        results = scheduler.start(create)
        assert results.messages == []

