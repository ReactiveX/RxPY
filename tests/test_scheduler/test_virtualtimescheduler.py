import unittest

import pytest

from reactivex.internal import ArgumentOutOfRangeException
from reactivex.internal.constants import DELTA_ZERO, UTC_ZERO
from reactivex.scheduler import VirtualTimeScheduler


class VirtualSchedulerTestScheduler(VirtualTimeScheduler):
    def add(self, absolute, relative):
        return absolute + relative


class TestVirtualTimeScheduler(unittest.TestCase):
    def test_virtual_now_noarg(self):
        scheduler = VirtualSchedulerTestScheduler()
        assert scheduler.clock == 0.0
        assert scheduler.now == UTC_ZERO

    def test_virtual_now_float(self):
        scheduler = VirtualSchedulerTestScheduler(0.0)
        assert scheduler.clock == 0.0
        assert scheduler.now == UTC_ZERO

    def test_virtual_now_timedelta(self):
        scheduler = VirtualSchedulerTestScheduler(DELTA_ZERO)
        assert scheduler.clock == DELTA_ZERO
        assert scheduler.now == UTC_ZERO

    def test_virtual_now_datetime(self):
        scheduler = VirtualSchedulerTestScheduler(UTC_ZERO)
        assert scheduler.clock == UTC_ZERO
        assert scheduler.now == UTC_ZERO

    def test_virtual_schedule_action(self):
        scheduler = VirtualSchedulerTestScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        scheduler.start()
        assert ran is True

    def test_virtual_schedule_action_error(self):
        scheduler = VirtualSchedulerTestScheduler()

        class MyException(Exception):
            pass

        def action(scheduler, state):
            raise MyException()

        with pytest.raises(MyException):
            scheduler.schedule(action)
            scheduler.start()

    def test_virtual_schedule_sleep_error(self):
        scheduler = VirtualSchedulerTestScheduler()

        with pytest.raises(ArgumentOutOfRangeException):
            scheduler.sleep(-1)

    def test_virtual_schedule_advance_clock_error(self):
        scheduler = VirtualSchedulerTestScheduler()

        with pytest.raises(ArgumentOutOfRangeException):
            scheduler.advance_to(scheduler._clock - 1)
