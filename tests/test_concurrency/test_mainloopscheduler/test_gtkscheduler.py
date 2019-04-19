from datetime import datetime, timedelta
import threading
import os
import unittest
import pytest

from rx.concurrency.mainloopscheduler import GtkScheduler

gi = pytest.importorskip("gi")
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk


# Removing GNOME_DESKTOP_SESSION_ID from environment
# prevents QtScheduler test from failing with message
#   Gtk-ERROR **: GTK+ 2.x symbols detected.
#   Using GTK+ 2.x and GTK+ 3 in the same process is not supported
if "GNOME_DESKTOP_SESSION_ID" in os.environ:
    del os.environ["GNOME_DESKTOP_SESSION_ID"]


class TestGtkScheduler(unittest.TestCase):

    def test_gtk_schedule_now(self):
        scheduler = GtkScheduler()
        res = scheduler.now - datetime.utcnow()
        assert(res < timedelta(seconds=1))

    def test_gtk_schedule_action(self):
        scheduler = GtkScheduler()
        gate = threading.Semaphore(0)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True
        scheduler.schedule(action)

        def done(data):
            Gtk.main_quit()
            gate.release()

        GLib.timeout_add(50, done, None)
        Gtk.main()

        gate.acquire()
        assert ran is True

    def test_gtk_schedule_action_relative(self):
        scheduler = GtkScheduler()
        gate = threading.Semaphore(0)
        starttime = datetime.utcnow()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.utcnow()

        scheduler.schedule_relative(0.1, action)

        def done(data):
            Gtk.main_quit()
            gate.release()

        GLib.timeout_add(200, done, None)
        Gtk.main()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=80)

    def test_gtk_schedule_action_absolute(self):
        scheduler = GtkScheduler()
        gate = threading.Semaphore(0)
        starttime = datetime.utcnow()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.utcnow()

        due = scheduler.now + timedelta(milliseconds=100)
        scheduler.schedule_absolute(due, action)

        def done(data):
            Gtk.main_quit()
            gate.release()

        GLib.timeout_add(200, done, None)
        Gtk.main()

        gate.acquire()
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=80)

    def test_gtk_schedule_action_cancel(self):
        ran = False
        scheduler = GtkScheduler()
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done(data):
            Gtk.main_quit()
            gate.release()

        GLib.timeout_add(200, done, None)
        Gtk.main()

        gate.acquire()
        assert ran is False

    def test_gtk_schedule_action_periodic(self):
        scheduler = GtkScheduler()
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter)

        def done(data):
            Gtk.main_quit()
            gate.release()

        GLib.timeout_add(300, done, None)
        Gtk.main()

        gate.acquire()
        assert counter == 0
