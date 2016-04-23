import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindow(unittest.TestCase):

    def test_window_closings_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_completed(590))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map(selector).merge_observable()

        results = scheduler.start(create=create, disposed=400)

        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"))
        xs.subscriptions.assert_equal(subscribe(200, 400))


    def test_window_closings_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_error(590, ex))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_error(590, ex))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]

        def create():
            def closing():
                raise Exception(ex)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(200, ex))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    def test_window_closings_window_close_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = 1

        def create():
            def closing():
                return Observable.throw_exception(ex, scheduler=scheduler)
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(201, ex))
        xs.subscriptions.assert_equal(subscribe(200, 201))

    def test_window_closings_default(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]

        def create():
            def closings():
                w = window[0]
                window[0] += 1
                return Observable.timer(w * 100, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(window_closing_selector=closings).map(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_completed(590))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_opening_closings_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))

        def create():
            def closing(x):
                return Observable.timer(x, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_next(420, "1 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(900))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        ys.subscriptions.assert_equal(subscribe(200, 900))

    def test_window_opening_closings_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))

        def create():
            def closing(x):
                raise Exception(ex)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(255, ex))
        xs.subscriptions.assert_equal(subscribe(200, 255))
        ys.subscriptions.assert_equal(subscribe(200, 255))

    def test_window_opening_closings_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))

        def create():
            def closing(x):
                return Observable.timer(x, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map(selector).merge_observable()
        results = scheduler.start(create=create, disposed=415)
        results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_opening_closings_data_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_error(415, ex))
        ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))

        def create():
            def closing(x):
                return Observable.timer(x, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map(selector).merge_observable()
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_error(415, ex))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_opening_closings_window_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_error(415, ex))
        def create():
            def closing(x):
                return Observable.timer(x, scheduler=scheduler)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map(selector).merge_observable()
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_error(415, ex))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_boundaries_simple(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_next(400, True),
            on_next(500, True),
            on_completed(900)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map(selector).merge_observable()
        res = scheduler.start(create=create)

        res.messages.assert_equal(
            on_next(250, "0 3"),
            on_next(260, "1 4"),
            on_next(310, "1 5"),
            on_next(340, "2 6"),
            on_next(410, "4 7"),
            on_next(420, "4 8"),
            on_next(470, "4 9"),
            on_next(550, "5 10"),
            on_completed(590)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 590)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 590)
        )

    def test_window_boundaries_on_completed_boundaries(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                on_next(90, 1),
                on_next(180, 2),
                on_next(250, 3),
                on_next(260, 4),
                on_next(310, 5),
                on_next(340, 6),
                on_next(410, 7),
                on_next(420, 8),
                on_next(470, 9),
                on_next(550, 10),
                on_completed(590)
        )

        ys = scheduler.create_hot_observable(
                on_next(255, True),
                on_next(330, True),
                on_next(350, True),
                on_completed(400)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map(selector).merge_observable()

        res = scheduler.start(create=create)

        res.messages.assert_equal(
                on_next(250, "0 3"),
                on_next(260, "1 4"),
                on_next(310, "1 5"),
                on_next(340, "2 6"),
                on_completed(400)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

    def test_window_boundaries_on_errorSource(self):
        ex = 'ex'
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                on_next(90, 1),
                on_next(180, 2),
                on_next(250, 3),
                on_next(260, 4),
                on_next(310, 5),
                on_next(340, 6),
                on_next(380, 7),
                on_error(400, ex)
        )

        ys = scheduler.create_hot_observable(
                on_next(255, True),
                on_next(330, True),
                on_next(350, True),
                on_completed(500)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map(selector).merge_observable()
        res = scheduler.start(create=create)

        res.messages.assert_equal(
                on_next(250, "0 3"),
                on_next(260, "1 4"),
                on_next(310, "1 5"),
                on_next(340, "2 6"),
                on_next(380, "3 7"),
                on_error(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

    def test_window_boundaries_on_error_boundaries(self):
        ex = 'ex'
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                on_next(90, 1),
                on_next(180, 2),
                on_next(250, 3),
                on_next(260, 4),
                on_next(310, 5),
                on_next(340, 6),
                on_next(410, 7),
                on_next(420, 8),
                on_next(470, 9),
                on_next(550, 10),
                on_completed(590)
        )

        ys = scheduler.create_hot_observable(
                on_next(255, True),
                on_next(330, True),
                on_next(350, True),
                on_error(400, ex)
        )
        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map(selector).merge_observable()

        res = scheduler.start(create=create)

        res.messages.assert_equal(
                on_next(250, "0 3"),
                on_next(260, "1 4"),
                on_next(310, "1 5"),
                on_next(340, "2 6"),
                on_error(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

if __name__ == '__main__':
    unittest.main()
