import datetime
import unittest

import rx
from rx.core import notification
from rx.core.observable.marbles import parse
from rx.testing import TestScheduler
from rx.testing.reactivetest import ReactiveTest


def mess_on_next(time, value):
    return (time, notification.OnNext(value))


def mess_on_error(time, error):
    return (time, notification.OnError(error))


def mess_on_completed(time):
    return (time, notification.OnCompleted())


class TestParse(unittest.TestCase):
    def test_parse_just_on_error(self):
        string = "#"
        results = parse(string)
        expected = [mess_on_error(0.0, Exception("error"))]
        assert results == expected

    def test_parse_just_on_error_specified(self):
        string = "#"
        ex = Exception("Foo")
        results = parse(string, error=ex)
        expected = [mess_on_error(0.0, ex)]
        assert results == expected

    def test_parse_just_on_completed(self):
        string = "|"
        results = parse(string)
        expected = [mess_on_completed(0.0)]
        assert results == expected

    def test_parse_just_on_next(self):
        string = "a"
        results = parse(string)
        expected = [mess_on_next(0.0, "a")]
        assert results == expected

    def test_parse_marble_timespan(self):
        string = "a--b---c"
        "         012345678901234567890"
        ts = 0.1
        results = parse(string, timespan=ts)
        expected = [
            mess_on_next(0 * ts, "a"),
            mess_on_next(3 * ts, "b"),
            mess_on_next(7 * ts, "c"),
        ]
        assert results == expected

    def test_parse_marble_timedelta(self):
        string = "a--b---c"
        "         012345678901234567890"
        ts = 0.1
        results = parse(string, timespan=datetime.timedelta(seconds=ts))
        expected = [
            mess_on_next(0 * ts, "a"),
            mess_on_next(3 * ts, "b"),
            mess_on_next(7 * ts, "c"),
        ]
        assert results == expected

    def test_parse_marble_multiple_digits(self):
        string = "-ab-cde--"
        "         012345678901234567890"
        results = parse(string)
        expected = [
            mess_on_next(1.0, "ab"),
            mess_on_next(4.0, "cde"),
        ]
        assert results == expected

    def test_parse_marble_multiple_digits_int(self):
        string = "-1-22-333-"
        "         012345678901234567890"
        results = parse(string)
        expected = [
            mess_on_next(1.0, 1),
            mess_on_next(3.0, 22),
            mess_on_next(6.0, 333),
        ]
        assert results == expected

    def test_parse_marble_multiple_digits_float(self):
        string = "-1.0--2.345--6.7e8-"
        "         012345678901234567890"
        results = parse(string)
        expected = [
            mess_on_next(1.0, float("1.0")),
            mess_on_next(6.0, float("2.345")),
            mess_on_next(13.0, float("6.7e8")),
        ]
        assert results == expected

    def test_parse_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        results = parse(string)
        expected = [
            mess_on_next(1.0, "ab"),
            mess_on_next(4.0, "c"),
            mess_on_completed(7.0),
        ]
        assert results == expected

    def test_parse_marble_with_error(self):
        string = "-a-b-c--#--"
        "         012345678901234567890"
        ex = Exception("ex")
        results = parse(string, error=ex)
        expected = [
            mess_on_next(1.0, "a"),
            mess_on_next(3.0, "b"),
            mess_on_next(5.0, "c"),
            mess_on_error(8.0, ex),
        ]
        assert results == expected

    def test_parse_marble_with_space(self):
        string = " -a  b- c-  de |"
        "          01  23 45  67 8901234567890"
        results = parse(string)
        expected = [
            mess_on_next(1.0, "ab"),
            mess_on_next(4.0, "c"),
            mess_on_next(6.0, "de"),
            mess_on_completed(8.0),
        ]
        assert results == expected

    def test_parse_marble_with_group(self):
        string = "-x(ab,12,1.5)-c--(de)-|"
        "         012345678901234567890123"
        "         0         1         2   "
        results = parse(string)
        expected = [
            mess_on_next(1.0, "x"),
            mess_on_next(2.0, "ab"),
            mess_on_next(2.0, 12),
            mess_on_next(2.0, float("1.5")),
            mess_on_next(14.0, "c"),
            mess_on_next(17.0, "de"),
            mess_on_completed(22.0),
        ]
        assert results == expected

    def test_parse_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            "ab": "aabb",
            "c": "cc",
            12: "1122",
            3: 33,
        }

        results = parse(string, lookup=lookup)
        expected = [
            mess_on_next(1.0, "aabb"),
            mess_on_next(4.0, "cc"),
            mess_on_next(6.0, "1122"),
            mess_on_next(9.0, 33),
            mess_on_completed(11.0),
        ]
        assert results == expected

    def test_parse_marble_time_shift(self):
        string = "-ab----c-d-|"
        "         012345678901234567890"
        offset = 10.0
        results = parse(string, time_shift=offset)
        expected = [
            mess_on_next(1.0 + offset, "ab"),
            mess_on_next(7.0 + offset, "c"),
            mess_on_next(9.0 + offset, "d"),
            mess_on_completed(11.0 + offset),
        ]
        assert results == expected

    def test_parse_marble_raise_with_elements_after_error(self):
        string = "-a-b-c--#-1-"
        "         012345678901234567890"
        with self.assertRaises(ValueError):
            parse(string, raise_stopped=True)

    def test_parse_marble_raise_with_elements_after_completed(self):
        string = "-a-b-c--|-1-"
        "         012345678901234567890"
        with self.assertRaises(ValueError):
            parse(string, raise_stopped=True)

    def test_parse_marble_raise_with_elements_after_completed_group(self):
        string = "-a-b-c--(|,1)-"
        "         012345678901234567890"
        with self.assertRaises(ValueError):
            parse(string, raise_stopped=True)

    def test_parse_marble_raise_with_elements_after_error_group(self):
        string = "-a-b-c--(#,1)-"
        "         012345678901234567890"
        with self.assertRaises(ValueError):
            parse(string, raise_stopped=True)


class TestFromMarble(unittest.TestCase):
    def create_factory(self, observable):
        def create():
            return observable

        return create

    def test_from_marbles_on_error(self):
        string = "#"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages

        expected = [ReactiveTest.on_error(200.0, Exception("error"))]
        assert results == expected

    def test_from_marbles_on_error_specified(self):
        string = "#"
        ex = Exception("Foo")
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages

        expected = [ReactiveTest.on_error(200.0, ex)]
        assert results == expected

    def test_from_marbles_on_complete(self):
        string = "|"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_completed(200.0)]
        assert results == expected

    def test_from_marbles_on_next(self):
        string = "a"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_next(200.0, "a")]
        assert results == expected

    def test_from_marbles_timespan(self):
        string = "a--b---c"
        "         012345678901234567890"
        ts = 0.5
        obs = rx.from_marbles(string, timespan=ts)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(0 * ts + 200.0, "a"),
            ReactiveTest.on_next(3 * ts + 200.0, "b"),
            ReactiveTest.on_next(7 * ts + 200.0, "c"),
        ]
        assert results == expected

    def test_from_marbles_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_completed(200.7),
        ]
        assert results == expected

    def test_from_marbles_marble_with_error(self):
        string = "-ab-c--#--"
        "         012345678901234567890"
        ex = Exception("ex")
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_error(200.7, ex),
        ]
        assert results == expected

    def test_from_marbles_marble_with_consecutive_symbols(self):
        string = "-ab(12)#--"
        "         012345678901234567890"
        ex = Exception("ex")
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.3, 12),
            ReactiveTest.on_error(200.7, ex),
        ]
        assert results == expected

    def test_from_marbles_marble_with_space(self):
        string = " -a  b- c-  - |"
        "          01  23 45  6 78901234567890"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_completed(200.7),
        ]
        assert results == expected

    def test_from_marbles_marble_with_group(self):
        string = "-(ab)-c-(12.5,def)--(6,|)"
        "         012345678901234567890"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.6, "c"),
            ReactiveTest.on_next(200.8, str(12.5)),
            ReactiveTest.on_next(200.8, "def"),
            ReactiveTest.on_next(202.0, 6),
            ReactiveTest.on_completed(202.0),
        ]
        assert results == expected

    def test_from_marbles_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            "ab": "aabb",
            "c": "cc",
            12: "1122",
            3: 33,
        }
        obs = rx.from_marbles(string, lookup=lookup)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "aabb"),
            ReactiveTest.on_next(200.4, "cc"),
            ReactiveTest.on_next(200.6, "1122"),
            ReactiveTest.on_next(200.9, 33),
            ReactiveTest.on_completed(201.1),
        ]
        assert results == expected

    def test_from_marbles_reuse(self):
        string = "a--b---c--|"
        "         012345678901234567890"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.0, "a"),
            ReactiveTest.on_next(200.3, "b"),
            ReactiveTest.on_next(200.7, "c"),
            ReactiveTest.on_completed(201.0),
        ]
        assert results == expected

        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.0, "a"),
            ReactiveTest.on_next(200.3, "b"),
            ReactiveTest.on_next(200.7, "c"),
            ReactiveTest.on_completed(201.0),
        ]
        assert results == expected

        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.0, "a"),
            ReactiveTest.on_next(200.3, "b"),
            ReactiveTest.on_next(200.7, "c"),
            ReactiveTest.on_completed(201.0),
        ]
        assert results == expected


class TestHot(unittest.TestCase):
    def create_factory(self, observable):
        def create():
            return observable

        return create

    def test_hot_on_error(self):
        string = "#"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.1, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages

        expected = [ReactiveTest.on_error(200.1, Exception("error"))]
        assert results == expected

    def test_hot_on_error_specified(self):
        string = "#"
        ex = Exception("Foo")
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.1, error=ex, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages

        expected = [ReactiveTest.on_error(200.1, ex)]
        assert results == expected

    def test_hot_on_complete(self):
        string = "|"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.1, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_completed(200.1)]
        assert results == expected

    def test_hot_on_next(self):
        string = "a"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.1, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_next(200.1, "a")]
        assert results == expected

    def test_hot_skipped_at_200(self):
        string = "a"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = []
        assert results == expected

    def test_hot_timespan(self):
        string = "-a-b---c"
        "         012345678901234567890"
        ts = 0.5
        scheduler = TestScheduler()
        obs = rx.hot(string, ts, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(1 * ts + 200.0, "a"),
            ReactiveTest.on_next(3 * ts + 200.0, "b"),
            ReactiveTest.on_next(7 * ts + 200.0, "c"),
        ]
        assert results == expected

    def test_hot_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_completed(200.7),
        ]
        assert results == expected

    def test_hot_marble_with_error(self):
        string = "-ab-c--#--"
        "         012345678901234567890"
        ex = Exception("ex")
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, error=ex, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_error(200.7, ex),
        ]
        assert results == expected

    def test_hot_marble_with_consecutive_symbols(self):
        string = "-ab(12)#--"
        "         012345678901234567890"
        ex = Exception("ex")
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, error=ex, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.3, 12),
            ReactiveTest.on_error(200.7, ex),
        ]
        assert results == expected

    def test_hot_marble_with_space(self):
        string = " -a  b- c-  - |"
        "          01  23 45  6 78901234567890"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.4, "c"),
            ReactiveTest.on_completed(200.7),
        ]
        assert results == expected

    def test_hot_marble_with_group(self):
        string = "-(ab)-c-(12.5,def)--(6,|)"
        "         01234567890123456789012345"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "ab"),
            ReactiveTest.on_next(200.6, "c"),
            ReactiveTest.on_next(200.8, str(12.5)),
            ReactiveTest.on_next(200.8, "def"),
            ReactiveTest.on_next(202.0, 6),
            ReactiveTest.on_completed(202.0),
        ]
        assert results == expected

    def test_hot_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            "ab": "aabb",
            "c": "cc",
            12: "1122",
            3: 33,
        }
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, lookup=lookup, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(200.1, "aabb"),
            ReactiveTest.on_next(200.4, "cc"),
            ReactiveTest.on_next(200.6, "1122"),
            ReactiveTest.on_next(200.9, 33),
            ReactiveTest.on_completed(201.1),
        ]
        assert results == expected

    def test_hot_marble_with_datetime(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        scheduler = TestScheduler()
        duetime = scheduler.now + datetime.timedelta(seconds=300.0)

        obs = rx.hot(string, 0.1, duetime, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(300.1, "ab"),
            ReactiveTest.on_next(300.4, "c"),
            ReactiveTest.on_completed(300.7),
        ]
        assert results == expected

    def test_hot_marble_with_timedelta(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        scheduler = TestScheduler()
        duetime = datetime.timedelta(seconds=300.0)

        obs = rx.hot(string, 0.1, duetime, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(300.1, "ab"),
            ReactiveTest.on_next(300.4, "c"),
            ReactiveTest.on_completed(300.7),
        ]
        assert results == expected
