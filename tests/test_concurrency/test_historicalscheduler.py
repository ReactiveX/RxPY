import unittest
from datetime import datetime, timedelta

from rx.concurrency import HistoricalScheduler


def assert_equals(first, second):
    if len(first) != len(second):
        print("len(%d) != len(%d)" % (len(first), len(second)))
        assert(False)

    for i in range(len(first)):
        f = first[i]
        s = second[i]
        if hasattr(f, "assert_equals") and hasattr(s, "assert_equals"):
            assert(f.assert_equals(s))
        else:
            assert(f == s)


def time(days):
    dt = datetime(year=1979, month=10, day=31, hour=4, minute=30, second=15)
    dt = dt + timedelta(days=days)
    return dt


def from_days(days):
    return timedelta(days=days)


class Timestamped(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

    def assert_equals(self, other):
        if not other:
            return False

        return other.value == self.value and other.timestamp == self.timestamp

    def __str__(self):
        return "(%s, %s)" % (self.value, self.timestamp)

    def __repr__(self):
        return str(self)


class TestHistoricalScheduler(unittest.TestCase):

    def test_ctor(self):
        s = HistoricalScheduler()
        self.assertEqual(datetime.fromtimestamp(0), s.clock)
        self.assertEqual(False, s.is_enabled)

    def test_start_stop(self):
        s = HistoricalScheduler()
        list = []

        s.schedule_absolute(time(0), lambda sc,st: list.append(Timestamped(1, s.now)))
        s.schedule_absolute(time(1), lambda sc,st: list.append(Timestamped(2, s.now)))
        s.schedule_absolute(time(2), lambda sc,st: s.stop())
        s.schedule_absolute(time(3), lambda sc,st: list.append(Timestamped(3, s.now)))
        s.schedule_absolute(time(4), lambda sc,st: s.stop())
        s.schedule_absolute(time(5), lambda sc,st: s.start())
        s.schedule_absolute(time(6), lambda sc,st: list.append(Timestamped(4, s.now)))

        s.start()

        self.assertEqual(time(2), s.now)
        self.assertEqual(time(2), s.clock)

        s.start()

        self.assertEqual(time(4), s.now)
        self.assertEqual(time(4), s.clock)

        s.start()

        self.assertEqual(time(6), s.now)
        self.assertEqual(time(6), s.clock)

        s.start()

        self.assertEqual(time(6), s.now)
        self.assertEqual(time(6), s.clock)

        assert_equals(list, [
            Timestamped(1, time(0)),
            Timestamped(2, time(1)),
            Timestamped(3, time(3)),
            Timestamped(4, time(6))
        ])

    def test_order(self):
        s = HistoricalScheduler()

        list = []

        s.schedule_absolute(time(2), lambda a, b: list.append(Timestamped(2, s.now)))

        s.schedule_absolute(time(3), lambda a, b: list.append(Timestamped(3, s.now)))

        s.schedule_absolute(time(1), lambda a, b: list.append(Timestamped(0, s.now)))
        s.schedule_absolute(time(1), lambda a, b: list.append(Timestamped(1, s.now)))

        s.start()

        assert_equals(list, [
            Timestamped(0, time(1)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2)),
            Timestamped(3, time(3))
        ])

    def test_cancellation(self):
        s = HistoricalScheduler()

        list = []

        d = s.schedule_absolute(time(2), lambda a,b: list.append(Timestamped(2, s.now)))

        def action(scheduler, state):
            list.append(Timestamped(0, s.now))
            d.dispose()

        s.schedule_absolute(time(1), action)

        s.start()

        assert_equals(list, [
            Timestamped(0, time(1))
        ])

    def test_advance_to(self):
        s = HistoricalScheduler()

        list = []

        s.schedule_absolute(time(0), lambda a,b: list.append(Timestamped(0, s.now)) )
        s.schedule_absolute(time(1), lambda a,b: list.append(Timestamped(1, s.now)) )
        s.schedule_absolute(time(2), lambda a,b: list.append(Timestamped(2, s.now)) )
        s.schedule_absolute(time(10), lambda a,b: list.append(Timestamped(10, s.now)) )
        s.schedule_absolute(time(11), lambda a,b: list.append(Timestamped(11, s.now)) )

        s.advance_to(time(8))

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.advance_to(time(8))

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.schedule_absolute(time(7), lambda a, b: list.append(Timestamped(7, s.now)) )
        s.schedule_absolute(time(8), lambda a, b: list.append(Timestamped(8, s.now)) )

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.advance_to(time(10))

        self.assertEqual(time(10), s.now)
        self.assertEqual(time(10), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2)),
            Timestamped(7, time(8)),
            Timestamped(8, time(8)),
            Timestamped(10, time(10))
        ])

        s.advance_to(time(100))

        self.assertEqual(time(100), s.now)
        self.assertEqual(time(100), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2)),
            Timestamped(7, time(8)),
            Timestamped(8, time(8)),
            Timestamped(10, time(10)),
            Timestamped(11, time(11))
        ])

    def test_advance_by(self):
        s = HistoricalScheduler()

        list = []

        s.schedule_absolute(time(0), lambda a, b: list.append(Timestamped(0, s.now)))
        s.schedule_absolute(time(1), lambda a, b: list.append(Timestamped(1, s.now)))
        s.schedule_absolute(time(2), lambda a, b: list.append(Timestamped(2, s.now)))
        s.schedule_absolute(time(10), lambda a, b: list.append(Timestamped(10, s.now)))
        s.schedule_absolute(time(11), lambda a, b: list.append(Timestamped(11, s.now)))

        s.advance_by(time(8) - s.now)

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.schedule_absolute(time(7), lambda a, b: list.append(Timestamped(7, s.now)))
        s.schedule_absolute(time(8), lambda a, b: list.append(Timestamped(8, s.now)))

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.advance_by(timedelta(0))

        self.assertEqual(time(8), s.now)
        self.assertEqual(time(8), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2))
        ])

        s.advance_by(from_days(2))

        self.assertEqual(time(10), s.now)
        self.assertEqual(time(10), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2)),
            Timestamped(7, time(8)),
            Timestamped(8, time(8)),
            Timestamped(10, time(10))
        ])

        s.advance_by(from_days(90))

        self.assertEqual(time(100), s.now)
        self.assertEqual(time(100), s.clock)

        assert_equals(list, [
            Timestamped(0, time(0)),
            Timestamped(1, time(1)),
            Timestamped(2, time(2)),
            Timestamped(7, time(8)),
            Timestamped(8, time(8)),
            Timestamped(10, time(10)),
            Timestamped(11, time(11))
        ])

    def test_is_enabled(self):
        s = HistoricalScheduler()

        self.assertEqual(False, s.is_enabled)

        def action(scheduler, state):
            self.assertEqual(True, s.is_enabled)
            s.stop()
            self.assertEqual(False, s.is_enabled)

        s.schedule(action)

        self.assertEqual(False, s.is_enabled)

        s.start()

        self.assertEqual(False, s.is_enabled)

    def test_sleep1(self):
        now = datetime(year=1983, month=2, day=11, hour=12)

        s = HistoricalScheduler(now)

        s.sleep(from_days(1))

        self.assertEqual(now + from_days(1), s.clock)

    def test_sleep2(self):
        s = HistoricalScheduler()
        n = [0]

        def action(scheduler, state):
            s.sleep(timedelta(3 * 6000))
            n[0] += 1
            s.schedule_absolute(s.now + timedelta(6000), action)

        s.schedule_absolute(s.now + timedelta(6000), action)

        s.advance_to(s.now + timedelta(5 * 6000))

        self.assertEqual(2, n[0])
