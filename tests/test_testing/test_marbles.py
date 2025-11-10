import unittest

from reactivex.testing.marbles import marbles_testing
from reactivex.testing.reactivetest import ReactiveTest

# from reactivex.scheduler import timeout_scheduler, new_thread_scheduler

# marble sequences to test:
# tested_marbles = '0-1-(10)|', '0|', '(10)-(20)|', '(abc)-|'


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


class TestTestContext(unittest.TestCase):
    def test_start_with_cold_never(self) -> None:
        with marbles_testing() as (start, cold, _hot, _exp):
            obs = cold("----", None, None)
            "           012345678901234567890"

            def create():
                return obs

            results = start(create)
            expected: list[object] = []
            assert results == expected

    def test_start_with_cold_empty(self) -> None:
        with marbles_testing() as (start, cold, _hot, _exp):
            obs = cold("------|", None, None)
            "           012345678901234567890"

            def create():
                return obs

            results = start(create)
            expected = [ReactiveTest.on_completed(206)]
            assert results == expected

    def test_start_with_cold_normal(self) -> None:
        with marbles_testing() as (start, cold, _hot, _exp):
            obs = cold("12--3-|", None, None)
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

    def test_start_with_cold_no_create_function(self) -> None:
        with marbles_testing() as (start, cold, _hot, _exp):
            obs = cold("12--3-|", None, None)
            "           012345678901234567890"

            results = start(obs)
            expected = [
                ReactiveTest.on_next(200, 12),
                ReactiveTest.on_next(204, 3),
                ReactiveTest.on_completed(206),
            ]
            assert results == expected

    def test_start_with_hot_never(self) -> None:
        with marbles_testing() as (start, _cold, hot, _exp):
            obs = hot("------", None, None)
            "          012345678901234567890"

            def create():
                return obs

            results = start(create)
            expected: list[object] = []
            assert results == expected

    def test_start_with_hot_empty(self) -> None:
        with marbles_testing() as (start, _cold, hot, _exp):
            obs = hot("---|", None, None)
            "          012345678901234567890"

            def create():
                return obs

            results = start(create)
            expected = [
                ReactiveTest.on_completed(203),
            ]
            assert results == expected

    def test_start_with_hot_normal(self) -> None:
        with marbles_testing() as (start, _cold, hot, _exp):
            obs = hot("-12--3-|", None, None)
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

    def test_exp(self) -> None:
        with marbles_testing() as (_start, _cold, _hot, exp):
            results = exp("12--3--4--5-|", None, None)
            "              012345678901234567890"

            expected = [
                ReactiveTest.on_next(200, 12),
                ReactiveTest.on_next(204, 3),
                ReactiveTest.on_next(207, 4),
                ReactiveTest.on_next(210, 5),
                ReactiveTest.on_completed(212),
            ]
            assert results == expected

    def test_start_with_hot_and_exp(self) -> None:
        with marbles_testing() as (start, _cold, hot, exp):
            obs = hot("     --3--4--5-|", None, None)
            expected = exp("--3--4--5-|", None, None)
            "               012345678901234567890"

            def create():
                return obs

            results = start(create)
            assert results == expected

    def test_start_with_cold_and_exp(self) -> None:
        with marbles_testing() as (start, cold, _hot, exp):
            obs = cold("     12--3--4--5-|", None, None)
            expected = exp(" 12--3--4--5-|", None, None)
            "                012345678901234567890"

            def create():
                return obs

            results = start(create)
            assert results == expected

    def test_start_with_cold_and_exp_group(self) -> None:
        with marbles_testing() as (start, cold, _hot, exp):
            obs = cold("     12--(3,6.5)----(5,#)", None, None)
            expected = exp(" 12--(3,6.5)----(5,#)", None, None)
            "                012345678901234567890"

            def create():
                return obs

            results = start(create)
            assert results == expected
