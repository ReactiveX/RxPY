import pytest
import unittest

from datetime import timedelta
from time import sleep

from rx.concurrency.mainloopscheduler import PyGameScheduler
from rx.internal.basic import default_now


pygame = pytest.importorskip("pygame")


class TestPyGameScheduler(unittest.TestCase):

    def test_pygame_schedule_now(self):
        scheduler = PyGameScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_pygame_schedule_action(self):
        scheduler = PyGameScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        scheduler.run()

        assert ran is True

    def test_pygame_schedule_action_due_relative(self):
        scheduler = PyGameScheduler()
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
        scheduler = PyGameScheduler()
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
        scheduler = PyGameScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        sleep(0.2)
        scheduler.run()

        assert ran is False
