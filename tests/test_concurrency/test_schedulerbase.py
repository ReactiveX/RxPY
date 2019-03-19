import unittest
from datetime import timedelta

from rx.internal.constants import DELTA_ZERO, UTC_ZERO
from rx.concurrency.schedulerbase import SchedulerBase


class TestSchedulerBase(unittest.TestCase):

    def test_base_to_seconds(self):
        val = SchedulerBase.to_seconds(0.0)
        assert val == 0.0
        val = SchedulerBase.to_seconds(DELTA_ZERO)
        assert val == 0.0
        val = SchedulerBase.to_seconds(UTC_ZERO)
        assert val == 0.0

    def test_base_to_datetime(self):
        val = SchedulerBase.to_datetime(0.0)
        assert val == UTC_ZERO
        val = SchedulerBase.to_datetime(DELTA_ZERO)
        assert val == UTC_ZERO
        val = SchedulerBase.to_datetime(UTC_ZERO)
        assert val == UTC_ZERO

    def test_base_to_timedelta(self):
        val = SchedulerBase.to_timedelta(0.0)
        assert val == DELTA_ZERO
        val = SchedulerBase.to_timedelta(DELTA_ZERO)
        assert val == DELTA_ZERO
        val = SchedulerBase.to_timedelta(UTC_ZERO)
        assert val == DELTA_ZERO

    def test_base_normalize_float(self):
        val = SchedulerBase.normalize(-1.0)
        assert val == 0.0
        val = SchedulerBase.normalize(0.0)
        assert val == 0.0
        val = SchedulerBase.normalize(1.0)
        assert val == 1.0

    def test_base_normalize_delta(self):
        DELTA_ONE = timedelta(seconds=1.0)
        val = SchedulerBase.normalize(-DELTA_ONE)
        assert val == DELTA_ZERO
        val = SchedulerBase.normalize(DELTA_ZERO)
        assert val == DELTA_ZERO
        val = SchedulerBase.normalize(DELTA_ONE)
        assert val == DELTA_ONE


