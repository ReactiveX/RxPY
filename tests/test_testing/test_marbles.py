import rx
import unittest
from rx.testing import marbles, TestScheduler
from rx.concurrency import timeout_scheduler, new_thread_scheduler

# marble sequences to test:
tested_marbles = '0-1-(10)|', '0|', '(10)-(20)|', '(abc)-|'

def test_alias():
    assert rx.Observable.from_string == rx.Observable.from_marbles


class TestFromToMarbles(unittest.TestCase):
    def _run_test(self,
                  expected_results,
                  src_scheduler,
                  dest_scheduler=None,
                  tested_marbles=tested_marbles):
        '''helper method, running the actual tests with given schedulers'''
        dest_scheduler = dest_scheduler or src_scheduler
        for marbles, expected in zip(tested_marbles, expected_results):
            stream = rx.Observable.from_string(marbles, src_scheduler)
            result = stream.to_blocking().to_marbles(dest_scheduler)
            self.assertEqual(result, expected)

    def test_new_thread_scheduler(self):
        'this is the default scheduler'
        self._run_test(tested_marbles, new_thread_scheduler)

    def test_timeout_scheduler(self):
        self._run_test(tested_marbles, timeout_scheduler)

    def test_timeout_new_thread_scheduler(self):
        self._run_test(tested_marbles, timeout_scheduler, new_thread_scheduler)

    def test_new_thread_scheduler_timeout(self):
        self._run_test(tested_marbles, new_thread_scheduler, timeout_scheduler)

    def test_timeout_testscheduler(self):
        '''the test scheduler uses virtual time => `to_marbles` does not
           see the original delays.
        '''
        expected = [t.replace('-', '') for t in tested_marbles]
        self._run_test(expected, timeout_scheduler, TestScheduler())

    def test_newthread_testscheduler(self):
        '''the test scheduler uses virtual time => `to_marbles` does not
           see the original delays.
        '''
        expected = [t.replace('-', '') for t in tested_marbles]
        self._run_test(expected, new_thread_scheduler, TestScheduler())


