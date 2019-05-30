import unittest
from datetime import timedelta

from rx.internal.constants import DELTA_ZERO, UTC_ZERO
from rx.concurrency.scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def test_base_to_seconds(self):
        val = Scheduler.to_seconds(0.0)
        assert val == 0.0
        val = Scheduler.to_seconds(DELTA_ZERO)
        assert val == 0.0
        val = Scheduler.to_seconds(UTC_ZERO)
        assert val == 0.0

    def test_base_to_datetime(self):
        val = Scheduler.to_datetime(0.0)
        assert val == UTC_ZERO
        val = Scheduler.to_datetime(DELTA_ZERO)
        assert val == UTC_ZERO
        val = Scheduler.to_datetime(UTC_ZERO)
        assert val == UTC_ZERO

    def test_base_to_timedelta(self):
        val = Scheduler.to_timedelta(0.0)
        assert val == DELTA_ZERO
        val = Scheduler.to_timedelta(DELTA_ZERO)
        assert val == DELTA_ZERO
        val = Scheduler.to_timedelta(UTC_ZERO)
        assert val == DELTA_ZERO

    def test_base_normalize_float(self):
        val = Scheduler.normalize(-1.0)
        assert val == 0.0
        val = Scheduler.normalize(0.0)
        assert val == 0.0
        val = Scheduler.normalize(1.0)
        assert val == 1.0

    def test_base_normalize_delta(self):
        DELTA_ONE = timedelta(seconds=1.0)
        val = Scheduler.normalize(-DELTA_ONE)
        assert val == DELTA_ZERO
        val = Scheduler.normalize(DELTA_ZERO)
        assert val == DELTA_ZERO
        val = Scheduler.normalize(DELTA_ONE)
        assert val == DELTA_ONE


