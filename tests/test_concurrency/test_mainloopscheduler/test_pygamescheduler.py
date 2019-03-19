import unittest
from datetime import datetime, timedelta
from time import sleep
import pytest

pygame = pytest.importorskip("pygame")
from rx.concurrency.mainloopscheduler import PyGameScheduler


class TestPyGameScheduler(unittest.TestCase):

    def test_pygame_schedule_now(self):
        scheduler = PyGameScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(seconds=1)

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
        starttime = datetime.utcnow()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.utcnow()

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
        starttime = datetime.utcnow()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.utcnow()

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
