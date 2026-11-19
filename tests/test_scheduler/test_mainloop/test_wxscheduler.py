import unittest
from datetime import datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler.mainloop import WxScheduler

wx: Any = pytest.importorskip("wx")


def make_app() -> Any:
    app = wx.App()
    wx.Frame(None)  # We need this for some reason, or the loop won't run
    return app


class AppExit(wx.Timer):
    def __init__(self, app: Any) -> None:
        super().__init__()  # pyright: ignore[reportUnknownMemberType]
        self.app = app

    def Notify(self) -> None:
        self.app.ExitMainLoop()


class TestWxScheduler(unittest.TestCase):
    def test_wx_schedule_now(self) -> None:
        scheduler = WxScheduler(wx)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_wx_schedule_now_units(self) -> None:
        scheduler = WxScheduler(wx)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action(self) -> None:
        app = make_app()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        exit.Start(100, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert ran is True

    def test_wx_schedule_action_relative(self) -> None:
        app = make_app()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.1, action)
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert endtime is not None
        diff = endtime - starttime
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action_absolute(self) -> None:
        app = make_app()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = default_now()

        due = scheduler.now + timedelta(milliseconds=100)
        scheduler.schedule_absolute(due, action)
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert endtime is not None
        diff = endtime - starttime
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action_cancel(self) -> None:
        app = make_app()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert ran is False

    def test_wx_schedule_action_periodic(self) -> None:
        app = make_app()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        period = 0.05
        counter = 3

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            return None

        scheduler.schedule_periodic(period, action, counter)
        exit.Start(500, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert counter == 0
