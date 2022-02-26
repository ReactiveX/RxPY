import unittest
from datetime import timedelta
from time import sleep

import pytest

from rx.internal.basic import default_now
from rx.scheduler.mainloop import PyGameScheduler

pygame = pytest.importorskip("pygame")


class TestPyGameScheduler(unittest.TestCase):
    def test_pygame_schedule_now(self):
        scheduler = PyGameScheduler(pygame)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_pygame_schedule_now_units(self):
        scheduler = PyGameScheduler(pygame)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_pygame_schedule_action(self):
        scheduler = PyGameScheduler(pygame)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        scheduler.run()

        assert ran is True

    def test_pygame_schedule_action_due_relative(self):
        scheduler = PyGameScheduler(pygame)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.1, action)

        scheduler.run()

        assert endtime is None

        sleep(0.2)
        scheduler.run()

        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_pygame_schedule_action_due_absolute(self):
        scheduler = PyGameScheduler(pygame)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_absolute(starttime + timedelta(seconds=0.1), action)

        scheduler.run()

        assert endtime is None

        sleep(0.2)
        scheduler.run()

        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_pygame_schedule_action_cancel(self):
        scheduler = PyGameScheduler(pygame)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        sleep(0.2)
        scheduler.run()

        assert ran is False
