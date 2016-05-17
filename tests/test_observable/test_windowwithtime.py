import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithTime(unittest.TestCase):

    def test_window_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(270, 4),
            on_next(320, 5),
            on_next(360, 6),
            on_next(390, 7),
            on_next(410, 8),
            on_next(460, 9),
            on_next(470, 10),
            on_completed(490)
        )

        def create():
            def selector(ys, i):
                def proj(y):
                    return "%s %s" % (i, y)
                return ys.map(proj).concat(Observable.return_value('%s end' % i))
            return xs.window_with_time(100, scheduler=scheduler).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, "0 2"),
            on_next(240, "0 3"),
            on_next(270, "0 4"),
            on_next(300, "0 end"),
            on_next(320, "1 5"),
            on_next(360, "1 6"),
            on_next(390, "1 7"),
            on_next(400, "1 end"),
            on_next(410, "2 8"),
            on_next(460, "2 9"),
            on_next(470, "2 10"),
            on_next(490, "2 end"),
            on_completed(490)
        )
        xs.subscriptions.assert_equal(subscribe(200, 490))

    def test_window_time_basic_both(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(270, 4),
            on_next(320, 5),
            on_next(360, 6),
            on_next(390, 7),
            on_next(410, 8),
            on_next(460, 9),
            on_next(470, 10),
            on_completed(490)
        )

        def create():
            def selector(ys, i):
                def proj(y):
                    return "%s %s" % (i, y)

                return ys.map(proj).concat(Observable.return_value('%s end' % i))
            return xs.window_with_time(100, 50, scheduler).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(270, "0 4"), on_next(270, "1 4"), on_next(300, "0 end"), on_next(320, "1 5"), on_next(320, "2 5"), on_next(350, "1 end"), on_next(360, "2 6"), on_next(360, "3 6"), on_next(390, "2 7"), on_next(390, "3 7"), on_next(400, "2 end"), on_next(410, "3 8"), on_next(410, "4 8"), on_next(450, "3 end"), on_next(460, "4 9"), on_next(460, "5 9"), on_next(470, "4 10"), on_next(470, "5 10"), on_next(490, "4 end"), on_next(490, "5 end"), on_completed(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))

    def test_window_with_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70, scheduler=scheduler).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_window_with_time_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70, scheduler=scheduler).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_error(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_Window_with_time_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, 70, scheduler=scheduler).map(selector).merge_observable()

        results = scheduler.start(create, disposed=370)
        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"))
        xs.subscriptions.assert_equal(subscribe(200, 370))

    def test_window_with_time_basic_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))


        def create():
            def selector(w, i):
                return w.map(lambda x: "%s %s" % (i, x))

            return xs.window_with_time(100, scheduler=scheduler).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(380, "1 7"), on_next(420, "2 8"), on_next(470, "2 9"), on_completed(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
