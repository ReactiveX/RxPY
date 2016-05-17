import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithCount(unittest.TestCase):
    def test_window_with_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
        def create():
            def proj(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window_with_count(3, 2).map(proj).merge_observable()
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_window_with_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

        def create():
            def proj(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window_with_count(3, 2).map(proj).merge_observable()

        results = scheduler.start(create, disposed=370)
        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"))
        xs.subscriptions.assert_equal(subscribe(200, 370))

    def test_window_with_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))

        def create():
            def selector(w, i):
                def mapping(x):
                    return "%s %s" % (i, x)
                return w.map(mapping)
            return xs.window_with_count(3, 2).map(selector).merge_observable()

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_error(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))
