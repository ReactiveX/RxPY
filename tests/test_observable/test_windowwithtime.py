import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithTime(unittest.TestCase):

    def test_window_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(240, 3),
            send(270, 4),
            send(320, 5),
            send(360, 6),
            send(390, 7),
            send(410, 8),
            send(460, 9),
            send(470, 10),
            close(490)
        )

        def create():
            def selector(ys, i):
                def proj(y):
                    return "%s %s" % (i, y)
                return ys.map(proj).concat(Observable.return_value('%s end' % i))
            return xs.window_with_time(100).map_indexed(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(210, "0 2"),
            send(240, "0 3"),
            send(270, "0 4"),
            send(300, "0 end"),
            send(320, "1 5"),
            send(360, "1 6"),
            send(390, "1 7"),
            send(400, "1 end"),
            send(410, "2 8"),
            send(460, "2 9"),
            send(470, "2 10"),
            send(490, "2 end"),
            close(490)
        )
        xs.subscriptions.assert_equal(subscribe(200, 490))

    def test_window_time_basic_both(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(240, 3),
            send(270, 4),
            send(320, 5),
            send(360, 6),
            send(390, 7),
            send(410, 8),
            send(460, 9),
            send(470, 10),
            close(490)
        )

        def create():
            def selector(ys, i):
                def proj(y):
                    return "%s %s" % (i, y)

                return ys.map(proj).concat(Observable.return_value('%s end' % i))
            return xs.window_with_time(100, 50).map_indexed(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, "0 2"), send(240, "0 3"), send(270, "0 4"), send(270, "1 4"), send(300, "0 end"), send(320, "1 5"), send(320, "2 5"), send(350, "1 end"), send(360, "2 6"), send(360, "3 6"), send(390, "2 7"), send(390, "3 7"), send(400, "2 end"), send(410, "3 8"), send(410, "4 8"), send(450, "3 end"), send(460, "4 9"), send(460, "5 9"), send(470, "4 10"), send(470, "5 10"), send(490, "4 end"), send(490, "5 end"), close(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))

    def test_window_with_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), close(600))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70).map_indexed(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6"), send(380, "2 7"), send(420, "2 8"), send(420, "3 8"), send(470, "3 9"), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_window_with_time_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), throw(600, ex))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70).map_indexed(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6"), send(380, "2 7"), send(420, "2 8"), send(420, "3 8"), send(470, "3 9"), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_Window_with_time_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), close(600))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70).map_indexed(selector).merge_observable()

        results = scheduler.start(create, disposed=370)
        results.messages.assert_equal(send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6"))
        xs.subscriptions.assert_equal(subscribe(200, 370))

    def test_window_with_time_basic_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), close(600))


        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100).map_indexed(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(320, "1 5"), send(350, "1 6"), send(380, "1 7"), send(420, "2 8"), send(470, "2 9"), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
