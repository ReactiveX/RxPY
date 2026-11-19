import threading
from collections.abc import Generator
from datetime import datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler.mainloop import QtScheduler

QtCore: Any = pytest.importorskip("PySide2.QtCore")


@pytest.fixture(scope="module")
def app() -> Generator[Any, None, None]:
    # share qt application among all tests
    app = QtCore.QCoreApplication([])
    yield app
    # teardown


class TestQtSchedulerPySide2:
    def test_pyside2_schedule_now(self) -> None:
        scheduler = QtScheduler(QtCore)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_pyside2_schedule_now_units(self) -> None:
        scheduler = QtScheduler(QtCore)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_pyside2_schedule_action(self, app: Any) -> None:
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(50, done)
        app.exec_()

        gate.acquire()
        assert ran is True

    def test_pyside2_schedule_action_due_relative(self, app: Any) -> None:
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.2, action)

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_pyside2_schedule_action_due_absolute(self, app: Any) -> None:
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_absolute(starttime + timedelta(seconds=0.2), action)

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_pyside2_schedule_action_cancel(self, app: Any) -> None:
        ran = False
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert ran is False

    def test_pyside2_schedule_action_periodic(self, app: Any) -> None:
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        period = 0.050
        counter = 3

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            return None

        scheduler.schedule_periodic(period, action, counter)

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert counter == 0

    def test_pyside2_schedule_periodic_cancel(self, app: Any) -> None:
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            return None

        disp = scheduler.schedule_periodic(period, action, counter)

        def dispose() -> None:
            disp.dispose()

        QtCore.QTimer.singleShot(100, dispose)

        def done() -> None:
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert 0 < counter < 3
