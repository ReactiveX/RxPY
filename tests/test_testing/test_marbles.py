import unittest

from rx.testing import marbles
from rx.testing.reactivetest import ReactiveTest

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
