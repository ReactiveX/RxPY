from datetime import datetime, timedelta
import os
import unittest

from nose import SkipTest

from rx.concurrency import GtkScheduler

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import GLib, Gtk
except ImportError:
    raise SkipTest("Need python-gi")


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
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        def done(data):
            Gtk.main_quit()
            assert ran[0]
            return False

        GLib.timeout_add(50, done, None)
        Gtk.main()

    def test_gtk_schedule_action_due(self):
        scheduler = GtkScheduler()
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()

        scheduler.schedule_relative(200, action)

        def done(data):
            Gtk.main_quit()
            assert endtime[0]
            diff = endtime[0] - starttime
            assert diff > timedelta(milliseconds=180)
            return False

        GLib.timeout_add(300, done, None)
        Gtk.main()

    def test_gtk_schedule_action_cancel(self):
        ran = [False]
        scheduler = GtkScheduler()

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(100, action)
        d.dispose()

        def done(data):
            Gtk.main_quit()
            assert not ran[0]
            return False

        GLib.timeout_add(300, done, None)
        Gtk.main()

    def test_gtk_schedule_action_periodic(self):
        scheduler = GtkScheduler()
        period = 50
        counter = [3]

        def action(state):
            if state:
                counter[0] -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter[0])

        def done(data):
            Gtk.main_quit()
            assert counter[0] == 0
            return False

        GLib.timeout_add(300, done, None)
        Gtk.main()
