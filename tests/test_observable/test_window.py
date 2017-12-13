import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindow(unittest.TestCase):

    def test_window_closings_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(send(250, "0 3"), send(260, "0 4"), send(310, "1 5"), send(340, "1 6"), send(410, "1 7"), send(420, "1 8"), send(470, "1 9"), send(550, "2 10"), close(590))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create, disposed=400)

        results.messages.assert_equal(send(250, "0 3"), send(260, "0 4"), send(310, "1 5"), send(340, "1 6"))
        xs.subscriptions.assert_equal(subscribe(200, 400))


    def test_window_closings_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), throw(590, ex))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(send(250, "0 3"), send(260, "0 4"), send(310, "1 5"), send(340, "1 6"), send(410, "1 7"), send(420, "1 8"), send(470, "1 9"), send(550, "2 10"), throw(590, ex))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        window = [1]

        def create():
            def closing():
                raise Exception(ex)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(200, ex))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    def test_window_closings_window_close_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        window = 1

        def create():
            def closing():
                return Observable.throw_exception(ex)
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(200, ex))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    def test_window_closings_default(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        window = [1]

        def create():
            def closings():
                w = window[0]
                window[0] += 1
                return Observable.timer(w * 100)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(window_closing_selector=closings).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(send(250, "0 3"), send(260, "0 4"), send(310, "1 5"), send(340, "1 6"), send(410, "1 7"), send(420, "1 8"), send(470, "1 9"), send(550, "2 10"), close(590))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_opening_closings_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        ys = scheduler.create_hot_observable(send(255, 50), send(330, 100), send(350, 50), send(400, 90), close(900))

        def create():
            def closing(x):
                return Observable.timer(x)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)
        results.messages.assert_equal(send(260, "0 4"), send(340, "1 6"), send(410, "1 7"), send(410, "3 7"), send(420, "1 8"), send(420, "3 8"), send(470, "3 9"), close(900))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        ys.subscriptions.assert_equal(subscribe(200, 900))

    def test_window_opening_closings_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        ys = scheduler.create_hot_observable(send(255, 50), send(330, 100), send(350, 50), send(400, 90), close(900))

        def create():
            def closing(x):
                raise Exception(ex)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map_indexed(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(255, ex))
        xs.subscriptions.assert_equal(subscribe(200, 255))
        ys.subscriptions.assert_equal(subscribe(200, 255))

    def test_window_opening_closings_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        ys = scheduler.create_hot_observable(send(255, 50), send(330, 100), send(350, 50), send(400, 90), close(900))

        def create():
            def closing(x):
                return Observable.timer(x)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map_indexed(selector).merge_observable()
        results = scheduler.start(create=create, disposed=415)
        results.messages.assert_equal(send(260, "0 4"), send(340, "1 6"), send(410, "1 7"), send(410, "3 7"))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_opening_closings_data_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), throw(415, ex))
        ys = scheduler.create_hot_observable(send(255, 50), send(330, 100), send(350, 50), send(400, 90), close(900))

        def create():
            def closing(x):
                return Observable.timer(x)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map_indexed(selector).merge_observable()
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(260, "0 4"), send(340, "1 6"), send(410, "1 7"), send(410, "3 7"), throw(415, ex))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_opening_closings_window_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, 1), send(180, 2), send(250, 3), send(260, 4), send(310, 5), send(340, 6), send(410, 7), send(420, 8), send(470, 9), send(550, 10), close(590))
        ys = scheduler.create_hot_observable(send(255, 50), send(330, 100), send(350, 50), send(400, 90), throw(415, ex))
        def create():
            def closing(x):
                return Observable.timer(x)

            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))

            return xs.window(ys, closing).map_indexed(selector).merge_observable()
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(260, "0 4"), send(340, "1 6"), send(410, "1 7"), send(410, "3 7"), throw(415, ex))
        xs.subscriptions.assert_equal(subscribe(200, 415))
        ys.subscriptions.assert_equal(subscribe(200, 415))

    def test_window_boundaries_simple(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(90, 1),
            send(180, 2),
            send(250, 3),
            send(260, 4),
            send(310, 5),
            send(340, 6),
            send(410, 7),
            send(420, 8),
            send(470, 9),
            send(550, 10),
            close(590)
        )

        ys = scheduler.create_hot_observable(
            send(255, True),
            send(330, True),
            send(350, True),
            send(400, True),
            send(500, True),
            close(900)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map_indexed(selector).merge_observable()
        res = scheduler.start(create=create)

        res.messages.assert_equal(
            send(250, "0 3"),
            send(260, "1 4"),
            send(310, "1 5"),
            send(340, "2 6"),
            send(410, "4 7"),
            send(420, "4 8"),
            send(470, "4 9"),
            send(550, "5 10"),
            close(590)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 590)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 590)
        )

    def test_window_boundaries_close_boundaries(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                send(90, 1),
                send(180, 2),
                send(250, 3),
                send(260, 4),
                send(310, 5),
                send(340, 6),
                send(410, 7),
                send(420, 8),
                send(470, 9),
                send(550, 10),
                close(590)
        )

        ys = scheduler.create_hot_observable(
                send(255, True),
                send(330, True),
                send(350, True),
                close(400)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map_indexed(selector).merge_observable()

        res = scheduler.start(create=create)

        res.messages.assert_equal(
                send(250, "0 3"),
                send(260, "1 4"),
                send(310, "1 5"),
                send(340, "2 6"),
                close(400)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

    def test_window_boundaries_throwSource(self):
        ex = 'ex'
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                send(90, 1),
                send(180, 2),
                send(250, 3),
                send(260, 4),
                send(310, 5),
                send(340, 6),
                send(380, 7),
                throw(400, ex)
        )

        ys = scheduler.create_hot_observable(
                send(255, True),
                send(330, True),
                send(350, True),
                close(500)
        )

        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map_indexed(selector).merge_observable()
        res = scheduler.start(create=create)

        res.messages.assert_equal(
                send(250, "0 3"),
                send(260, "1 4"),
                send(310, "1 5"),
                send(340, "2 6"),
                send(380, "3 7"),
                throw(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

    def test_window_boundaries_throw_boundaries(self):
        ex = 'ex'
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
                send(90, 1),
                send(180, 2),
                send(250, 3),
                send(260, 4),
                send(310, 5),
                send(340, 6),
                send(410, 7),
                send(420, 8),
                send(470, 9),
                send(550, 10),
                close(590)
        )

        ys = scheduler.create_hot_observable(
                send(255, True),
                send(330, True),
                send(350, True),
                throw(400, ex)
        )
        def create():
            def selector(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window(ys).map_indexed(selector).merge_observable()

        res = scheduler.start(create=create)

        res.messages.assert_equal(
                send(250, "0 3"),
                send(260, "1 4"),
                send(310, "1 5"),
                send(340, "2 6"),
                throw(400, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 400)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 400)
        )

if __name__ == '__main__':
    unittest.main()
