import unittest
from datetime import UTC, datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.scheduler.eventloop import IOLoopScheduler

tornado: Any = pytest.importorskip("tornado")
ioloop: Any = pytest.importorskip("tornado.ioloop")


class TestIOLoopScheduler(unittest.TestCase):
    def test_ioloop_schedule_now(self) -> None:
        loop = ioloop.IOLoop.instance()
        scheduler = IOLoopScheduler(loop)
        diff = scheduler.now - datetime.now(UTC)
        assert abs(diff) < timedelta(milliseconds=100)

    def test_ioloop_schedule_now_units(self) -> None:
        loop = ioloop.IOLoop.instance()
        scheduler = IOLoopScheduler(loop)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_ioloop_schedule_action(self) -> None:
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done() -> None:
            assert ran is True
            loop.stop()

        loop.call_later(0.1, done)
        loop.start()

    def test_ioloop_schedule_action_due(self) -> None:
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        starttime = loop.time()
        endtime = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = loop.time()

        scheduler.schedule_relative(0.2, action)

        def done() -> None:
            assert endtime is not None
            diff = endtime - starttime
            assert diff > 0.18
            loop.stop()

        loop.call_later(0.3, done)
        loop.start()

    def test_ioloop_schedule_action_absolute(self) -> None:
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        duetime = datetime.now(UTC) + timedelta(milliseconds=100)
        scheduler.schedule_absolute(duetime, action)

        def done() -> None:
            assert ran is True
            loop.stop()

        loop.call_later(0.3, done)
        loop.start()

    def test_ioloop_schedule_action_cancel(self) -> None:
        loop = ioloop.IOLoop.instance()

        ran = False
        scheduler = IOLoopScheduler(loop)

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        def done() -> None:
            assert ran is False
            loop.stop()

        loop.call_later(0.1, done)
        loop.start()
