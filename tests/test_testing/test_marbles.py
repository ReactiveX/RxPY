import rx
import unittest
from rx.testing import marbles, TestScheduler

class TestMarbles(unittest.TestCase):
    def test_alias(self):
        assert rx.Observable.from_string == rx.Observable.from_marbles

    def test_from_to_marbles(self):
        'using default scheduler'
        # GK: in the marbles test strings, always add a tick ("-") at the end,
        # when using the default scheduler.
        # Otherwise you might get intermittent(!) failures (missing last events).
        # Which breaks travis(!).
        # If unsure let it run a while, e.g. on bash:
        # `while true; do nosetests -w "tests/test_testing"  -sv || break; done`
        for marbles in '0-1-(10)-|', '0-|', '(10)-(20)-|', '(abc)-|':
            #from nose.tools import set_trace; set_trace()
            stream = rx.Observable.from_string(marbles)
            res = stream.to_blocking().to_marbles()
            self.assertEqual(res, marbles)



    def test_from_to_marbles_with_testscheduler(self):
        'using test scheduler'
        scheduler = TestScheduler()
        for marbles in '0-1-(10)-|', '0-|', '(10)-(20)-|', '(abc)-|':
            #from nose.tools import set_trace; set_trace()
            stream = rx.Observable.from_string(marbles)
            res = stream.to_blocking().to_marbles(scheduler=scheduler)
            # the test scheduler uses virtual time => `to_marbles` does not
            # see the original delays:
            self.assertEqual(res, marbles.replace('-', ''))




