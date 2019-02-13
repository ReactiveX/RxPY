import unittest
from datetime import datetime, timedelta
import pytest


skip = False
try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QApplication
except ImportError:
    try:
        from PyQt4 import QtCore
        from PyQt4.QtGui import QApplication
    except ImportError:
        try:
            from PySide2 import QtCore
            from PySide2.QtGui import QGuiApplication as QApplication
        except ImportError:
            skip = True


from rx.concurrency.mainloopscheduler import QtScheduler

app = None  # Prevent garbage collection


def make_app():
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.mark.skipif("skip == True")
class TestQtScheduler(unittest.TestCase):

    def test_qt_schedule_now(self):
        scheduler = QtScheduler(QtCore)
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(seconds=1)

    def test_qt_schedule_action(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        def done():
            app.quit()
            assert ran[0]

        QtCore.QTimer.singleShot(50, done)
        app.exec_()

    def test_qt_schedule_action_due(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()

        scheduler.schedule_relative(0.2, action)

        def done():
            app.quit()
            assert endtime[0]
            diff = endtime[0] - starttime
            assert diff > timedelta(milliseconds=180)

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

    def test_qt_schedule_action_cancel(self):
        app = make_app()

        ran = [False]
        scheduler = QtScheduler(QtCore)

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done():
            app.quit()
            assert not ran[0]

        QtCore.QTimer.singleShot(300, done)
        app.exec_()

    def test_qt_schedule_action_periodic(self):
        app = make_app()

        scheduler = QtScheduler(QtCore)
        period = 0.050
        counter = [3]

        def action(state):
            if state:
                counter[0] -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter[0])

        def done():
            app.quit()
            assert counter[0] == 0

        QtCore.QTimer.singleShot(300, done)
        app.exec_()
