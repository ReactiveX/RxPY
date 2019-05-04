import unittest
import threading
from datetime import timedelta
from time import sleep
import pytest


skip = False
try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QApplication
except ImportError:
    skip = True

if not skip:
    from rx.concurrency.mainloopscheduler import QtScheduler
    from rx.internal.basic import default_now


app = None  # Prevent garbage collection


def make_app():
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.mark.skipif("skip == True")
class TestQtSchedulerQt5(unittest.TestCase):

    def test_qt5_schedule_now(self):
        scheduler = QtScheduler(QtCore)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_qt5_schedule_now_units(self):
        scheduler = QtScheduler(QtCore)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_qt5_schedule_action(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(50, done)
        app.exec_()

        gate.acquire()
        assert ran is True

    def test_qt5_schedule_action_due_relative(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.2, action)

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_qt5_schedule_action_due_absolute(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_absolute(starttime + timedelta(seconds=0.2), action)

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_qt5_schedule_action_cancel(self):
        app = make_app()

        ran = False
        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert ran is False

    def test_qt5_schedule_action_periodic(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        period = 0.050
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter)

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert counter == 0

    def test_qt5_schedule_periodic_cancel(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        disp = scheduler.schedule_periodic(period, action, counter)

        def dispose():
            disp.dispose()

        QtCore.QTimer.singleShot(100, dispose)

        def done():
            app.quit()
            gate.release()

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

        gate.acquire()
        assert 0 < counter < 3
