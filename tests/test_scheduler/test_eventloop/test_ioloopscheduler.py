import unittest
from datetime import datetime, timedelta
from time import sleep

import pytest

from reactivex.scheduler.eventloop import IOLoopScheduler

tornado = pytest.importorskip("tornado")
from tornado import ioloop  # isort: skip


class TestIOLoopScheduler(unittest.TestCase):
    def test_ioloop_schedule_now(self):
        loop = ioloop.IOLoop.instance()
        scheduler = IOLoopScheduler(loop)
        diff = scheduler.now - datetime.utcfromtimestamp(loop.time())
        assert abs(diff) < timedelta(milliseconds=1)

    def test_ioloop_schedule_now_units(self):
        loop = ioloop.IOLoop.instance()
        scheduler = IOLoopScheduler(loop)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_ioloop_schedule_action(self):
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done():
            assert ran is True
            loop.stop()

        loop.call_later(0.1, done)
        loop.start()

    def test_ioloop_schedule_action_due(self):
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        starttime = loop.time()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = loop.time()

        scheduler.schedule_relative(0.2, action)

        def done():
            assert endtime is not None
            diff = endtime - starttime
            assert diff > 0.18
            loop.stop()

        loop.call_later(0.3, done)
        loop.start()

    def test_ioloop_schedule_action_cancel(self):
        loop = ioloop.IOLoop.instance()

        ran = False
        scheduler = IOLoopScheduler(loop)

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        def done():
            assert ran is False
            loop.stop()

        loop.call_later(0.1, done)
        loop.start()
