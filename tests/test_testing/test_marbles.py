import unittest

import rx
from rx.core.observable.marbles import parse
from rx import Observable
from rx.testing import TestScheduler, marbles
from rx.testing.reactivetest import ReactiveTest
from rx.core import notification

#from rx.concurrency import timeout_scheduler, new_thread_scheduler

# marble sequences to test:
#tested_marbles = '0-1-(10)|', '0|', '(10)-(20)|', '(abc)-|'


# class TestFromToMarbles(unittest.TestCase):

#     def test_new_thread_scheduler(self):
#         stream = Observable.from_marbles(marbles)
#         result = stream.to_blocking().to_marbles()
#         self.assertEqual(result, expected)

#         'this is the default scheduler'
#         self._run_test(tested_marbles, new_thread_scheduler)

    # def test_timeout_scheduler(self):
    #     self._run_test(tested_marbles, timeout_scheduler)

    # def test_timeout_new_thread_scheduler(self):
    #     self._run_test(tested_marbles, timeout_scheduler, new_thread_scheduler)

    # def test_new_thread_scheduler_timeout(self):
    #     self._run_test(tested_marbles, new_thread_scheduler, timeout_scheduler)

    # def test_timeout_testscheduler(self):
    #     '''the test scheduler uses virtual time => `to_marbles` does not
    #        see the original delays.
    #     '''
    #     expected = [t.replace('-', '') for t in tested_marbles]
    #     self._run_test(expected, timeout_scheduler, TestScheduler())

    # def test_newthread_testscheduler(self):
    #     '''the test scheduler uses virtual time => `to_marbles` does not
    #        see the original delays.
    #     '''
    #     expected = [t.replace('-', '') for t in tested_marbles]
    #     self._run_test(expected, new_thread_scheduler, TestScheduler())

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
        expected = [mess_on_error(0, Exception('error'))]
        assert results == expected

    def test_parse_just_on_error_specified(self):
        string = "#"
        ex = Exception('Foo')
        results = parse(string, error=ex)
        expected = [mess_on_error(0, ex)]
        assert results == expected

    def test_parse_just_on_completed(self):
        string = "|"
        results = parse(string)
        expected = [mess_on_completed(0)]
        assert results == expected

    def test_parse_just_on_next(self):
        string = "a"
        results = parse(string)
        expected = [mess_on_next(0, 'a')]
        assert results == expected

    def test_parse_marble_timespan(self):
        string = "a--b---c"
        "         012345678901234567890"
        ts = 0.1
        results = parse(string, timespan=ts)
        expected = [
            mess_on_next(0 * ts, 'a'),
            mess_on_next(3 * ts, 'b'),
            mess_on_next(7 * ts, 'c'),
            ]
        assert results == expected

    def test_parse_marble_multiple_digits(self):
        string = "-ab-cde--"
        "         012345678901234567890"
        results = parse(string)
        expected = [
                mess_on_next(1, 'ab'),
                mess_on_next(4, 'cde'),
                ]
        assert results == expected

    def test_parse_marble_multiple_digits_int(self):
        string = "-1-22-333-"
        "         012345678901234567890"
        results = parse(string)
        expected = [
                mess_on_next(1, 1),
                mess_on_next(3, 22),
                mess_on_next(6, 333),
                ]
        assert results == expected

    def test_parse_marble_multiple_digits_float(self):
        string = "-1.0--2.345--6.7e8-"
        "         012345678901234567890"
        results = parse(string)
        expected = [
                mess_on_next(1, float('1.0')),
                mess_on_next(6, float('2.345')),
                mess_on_next(13, float('6.7e8')),
                ]
        assert results == expected

    def test_parse_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        results = parse(string)
        expected = [
                mess_on_next(1, 'ab'),
                mess_on_next(4, 'c'),
                mess_on_completed(7),
                ]
        assert results == expected

    def test_parse_marble_with_error(self):
        string = "-a-b-c--#--"
        "         012345678901234567890"
        ex = Exception('ex')
        results = parse(string, error=ex)
        expected = [
                mess_on_next(1, 'a'),
                mess_on_next(3, 'b'),
                mess_on_next(5, 'c'),
                mess_on_error(8, ex),
                ]
        assert results == expected

    def test_parse_marble_with_space(self):
        string = " -a  b- c-  de |"
        "          01  23 45  67 8901234567890"
        results = parse(string)
        expected = [
                mess_on_next(1, 'ab'),
                mess_on_next(4, 'c'),
                mess_on_next(6, 'de'),
                mess_on_completed(8),
                ]
        assert results == expected

    def test_parse_marble_with_group(self):
        string = "-x(ab,12,1.5)-c--(de)-|"
        "         012345678901234567890123"
        "         0         1         2   "
        results = parse(string)
        expected = [
                mess_on_next(1, 'x'),
                mess_on_next(2, 'ab'),
                mess_on_next(2, 12),
                mess_on_next(2, float('1.5')),

                mess_on_next(14, 'c'),
                mess_on_next(17, 'de'),

                mess_on_completed(22),
                ]
        assert results == expected

    def test_parse_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            'ab': 'aabb',
            'c': 'cc',
            12: '1122',
            3: 33,
            }

        results = parse(string, lookup=lookup)
        expected = [
                mess_on_next(1, 'aabb'),
                mess_on_next(4, 'cc'),
                mess_on_next(6, '1122'),
                mess_on_next(9, 33),
                mess_on_completed(11),
                ]
        assert results == expected

    def test_parse_marble_time_shift(self):
        string = "-ab----c-d-|"
        "         012345678901234567890"
        offset = 10
        results = parse(string, time_shift=offset)
        expected = [
                mess_on_next(1 + offset, 'ab'),
                mess_on_next(7 + offset, 'c'),
                mess_on_next(9 + offset, 'd'),
                mess_on_completed(11 + offset),
                ]
        assert results == expected


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

        expected = [ReactiveTest.on_error(200, Exception('error'))]
        assert results == expected

    def test_from_marbles_on_error_specified(self):
        string = "#"
        ex = Exception('Foo')
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages

        expected = [ReactiveTest.on_error(200, ex)]
        assert results == expected

    def test_from_marbles_on_complete(self):
        string = "|"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_completed(200)]
        assert results == expected

    def test_from_marbles_on_next(self):
        string = "a"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [ReactiveTest.on_next(200, 'a')]
        assert results == expected

    def test_from_marbles_timespan(self):
        string = "a--b---c"
        "         012345678901234567890"
        ts = 0.5
        obs = rx.from_marbles(string, timespan=ts)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
            ReactiveTest.on_next(0 * ts + 200, 'a'),
            ReactiveTest.on_next(3 * ts + 200, 'b'),
            ReactiveTest.on_next(7 * ts + 200, 'c'),
            ]
        assert results == expected

    def test_from_marbles_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        obs = rx.from_marbles(string)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
                ReactiveTest.on_completed(200.7),
                ]
        assert results == expected

    def test_from_marbles_marble_with_error(self):
        string = "-ab-c--#--"
        "         012345678901234567890"
        ex = Exception('ex')
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
                ReactiveTest.on_error(200.7, ex),
                ]
        assert results == expected

    def test_from_marbles_marble_with_consecutive_symbols(self):
        string = "-ab(12)#--"
        "         012345678901234567890"
        ex = Exception('ex')
        obs = rx.from_marbles(string, error=ex)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
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
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
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
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.6, 'c'),
                ReactiveTest.on_next(200.8, str(12.5)),
                ReactiveTest.on_next(200.8, 'def'),
                ReactiveTest.on_next(202.0, 6),
                ReactiveTest.on_completed(202.0),
                ]
        assert results == expected

    def test_from_marbles_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            'ab': 'aabb',
            'c': 'cc',
            12: '1122',
            3: 33,
            }
        obs = rx.from_marbles(string, lookup=lookup)
        scheduler = TestScheduler()
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'aabb'),
                ReactiveTest.on_next(200.4, 'cc'),
                ReactiveTest.on_next(200.6, '1122'),
                ReactiveTest.on_next(200.9, 33),
                ReactiveTest.on_completed(201.1),
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

        expected = [ReactiveTest.on_error(200.1, Exception('error'))]
        assert results == expected

    def test_hot_on_error_specified(self):
        string = "#"
        ex = Exception('Foo')
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
        expected = [ReactiveTest.on_next(200.1, 'a')]
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
            ReactiveTest.on_next(1 * ts + 200.0, 'a'),
            ReactiveTest.on_next(3 * ts + 200.0, 'b'),
            ReactiveTest.on_next(7 * ts + 200.0, 'c'),
            ]
        assert results == expected

    def test_hot_marble_completed(self):
        string = "-ab-c--|"
        "         012345678901234567890"
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
                ReactiveTest.on_completed(200.7),
                ]
        assert results == expected

    def test_hot_marble_with_error(self):
        string = "-ab-c--#--"
        "         012345678901234567890"
        ex = Exception('ex')
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, error=ex, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
                ReactiveTest.on_error(200.7, ex),
                ]
        assert results == expected

    def test_from_marbles_marble_with_consecutive_symbols(self):
        string = "-ab(12)#--"
        "         012345678901234567890"
        ex = Exception('ex')
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, error=ex, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'ab'),
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
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.4, 'c'),
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
                ReactiveTest.on_next(200.1, 'ab'),
                ReactiveTest.on_next(200.6, 'c'),
                ReactiveTest.on_next(200.8, str(12.5)),
                ReactiveTest.on_next(200.8, 'def'),
                ReactiveTest.on_next(202.0, 6),
                ReactiveTest.on_completed(202.0),
                ]
        assert results == expected

    def test_hot_marble_lookup(self):
        string = "-ab-c-12-3-|"
        "         012345678901234567890"
        lookup = {
            'ab': 'aabb',
            'c': 'cc',
            12: '1122',
            3: 33,
            }
        scheduler = TestScheduler()
        obs = rx.hot(string, 0.1, 200.0, lookup=lookup, scheduler=scheduler)
        results = scheduler.start(self.create_factory(obs)).messages
        expected = [
                ReactiveTest.on_next(200.1, 'aabb'),
                ReactiveTest.on_next(200.4, 'cc'),
                ReactiveTest.on_next(200.6, '1122'),
                ReactiveTest.on_next(200.9, 33),
                ReactiveTest.on_completed(201.1),
                ]
        assert results == expected



class TestTestContext(unittest.TestCase):

    def test_start_with_cold_never(self):
        start, cold, hot, exp = marbles.test_context()
        obs = cold("----")
        "           012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = []
        assert results == expected

    def test_start_with_cold_empty(self):
        start, cold, hot, exp = marbles.test_context()
        obs = cold("------|")
        "           012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = [ReactiveTest.on_completed(206)]
        assert results == expected

    def test_start_with_cold_normal(self):
        start, cold, hot, exp = marbles.test_context()
        obs = cold("12--3-|")
        "           012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = [
            ReactiveTest.on_next(200, 12),
            ReactiveTest.on_next(204, 3),
            ReactiveTest.on_completed(206),
            ]
        assert results == expected

    def test_start_with_cold_no_create_function(self):
        start, cold, hot, exp = marbles.test_context()
        obs = cold("12--3-|")
        "           012345678901234567890"

        results = start(obs)
        expected = [
            ReactiveTest.on_next(200, 12),
            ReactiveTest.on_next(204, 3),
            ReactiveTest.on_completed(206),
            ]
        assert results == expected

    def test_start_with_hot_never(self):
        start, cold, hot, exp = marbles.test_context()
        obs = hot("------")
        "          012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = []
        assert results == expected

    def test_start_with_hot_empty(self):
        start, cold, hot, exp = marbles.test_context()
        obs = hot("---|")
        "          012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = [ReactiveTest.on_completed(203), ]
        assert results == expected

    def test_start_with_hot_normal(self):
        start, cold, hot, exp = marbles.test_context()
        obs = hot("-12--3-|")
        "          012345678901234567890"

        def create():
            return obs

        results = start(create)
        expected = [
            ReactiveTest.on_next(201, 12),
            ReactiveTest.on_next(205, 3),
            ReactiveTest.on_completed(207),
            ]
        assert results == expected

    def test_exp(self):
        start, cold, hot, exp = marbles.test_context()
        results = exp("12--3--4--5-|")
        "              012345678901234567890"

        expected = [
            ReactiveTest.on_next(200, 12),
            ReactiveTest.on_next(204, 3),
            ReactiveTest.on_next(207, 4),
            ReactiveTest.on_next(210, 5),
            ReactiveTest.on_completed(212),
            ]
        assert results == expected

    def test_start_with_hot_and_exp(self):

        start, cold, hot, exp = marbles.test_context()
        obs = hot("     --3--4--5-|")
        expected = exp("--3--4--5-|")
        "               012345678901234567890"

        def create():
            return obs

        results = start(create)
        assert results == expected

    def test_start_with_cold_and_exp(self):

        start, cold, hot, exp = marbles.test_context()
        obs = cold("     12--3--4--5-|")
        expected = exp(" 12--3--4--5-|")
        "                012345678901234567890"

        def create():
            return obs

        results = start(create)
        assert results == expected

    def test_start_with_cold_and_exp_group(self):

        start, cold, hot, exp = marbles.test_context()
        obs = cold("     12--(3,6.5)----(5,#)-e-|")
        expected = exp(" 12--(3,6.5)----(5,#)    ")
        "                012345678901234567890"

        def create():
            return obs

        results = start(create)
        assert results == expected
