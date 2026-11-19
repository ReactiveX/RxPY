import unittest
from datetime import datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler.mainloop import PyGameScheduler

pygame: Any = pytest.importorskip("pygame")


class TestPyGameScheduler(unittest.TestCase):
    def test_pygame_schedule_now(self) -> None:
        scheduler = PyGameScheduler(pygame)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_pygame_schedule_now_units(self) -> None:
        scheduler = PyGameScheduler(pygame)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_pygame_schedule_action(self) -> None:
        scheduler = PyGameScheduler(pygame)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        scheduler.run()

        assert ran is True

    def test_pygame_schedule_action_due_relative(self) -> None:
        scheduler = PyGameScheduler(pygame)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
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

    def test_pygame_schedule_action_due_absolute(self) -> None:
        scheduler = PyGameScheduler(pygame)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
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

    def test_pygame_schedule_action_cancel(self) -> None:
        scheduler = PyGameScheduler(pygame)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        sleep(0.2)
        scheduler.run()

        assert ran is False
