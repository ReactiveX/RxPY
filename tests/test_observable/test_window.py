import unittest

import rx
from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindow(unittest.TestCase):
    def test_window_when_basic(self):
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
            on_completed(590),
        )
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return rx.timer(curr * 100)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_when(closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)
        assert results.messages == [
            on_next(250, "0 3"),
            on_next(260, "0 4"),
            on_next(310, "1 5"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(420, "1 8"),
            on_next(470, "1 9"),
            on_next(550, "2 10"),
            on_completed(590),
        ]
        assert xs.subscriptions == [subscribe(200, 590)]

    def test_window_when_dispose(self):
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
            on_completed(590),
        )
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return rx.timer(curr * 100)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_when(closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create, disposed=400)

        assert results.messages == [
            on_next(250, "0 3"),
            on_next(260, "0 4"),
            on_next(310, "1 5"),
            on_next(340, "1 6"),
        ]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_window_when_error(self):
        ex = "ex"
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
            on_error(590, ex),
        )
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return rx.timer(curr * 100)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_when(closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(250, "0 3"),
            on_next(260, "0 4"),
            on_next(310, "1 5"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(420, "1 8"),
            on_next(470, "1 9"),
            on_next(550, "2 10"),
            on_error(590, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 590)]

    def test_window_when_on_error(self):
        ex = "ex"
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
            on_completed(590),
        )

        def create():
            def closing():
                raise Exception(ex)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_when(closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [on_error(200, ex)]
        assert xs.subscriptions == [subscribe(200, 200)]

    def test_window_when_window_close_error(self):
        ex = "ex"
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
            on_completed(590),
        )

        def create():
            def closing():
                return rx.throw(ex)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_when(closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [on_error(200, ex)]
        assert xs.subscriptions == [subscribe(200, 200)]

    def test_window_toggle_basic(self):
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
            on_completed(590),
        )
        ys = scheduler.create_hot_observable(
            on_next(255, 50),
            on_next(330, 100),
            on_next(350, 50),
            on_next(400, 90),
            on_completed(900),
        )

        def create():
            def closing(x):
                return rx.timer(x)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_toggle(ys, closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)
        assert results.messages == [
            on_next(260, "0 4"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(410, "3 7"),
            on_next(420, "1 8"),
            on_next(420, "3 8"),
            on_next(470, "3 9"),
            on_completed(900),
        ]
        assert xs.subscriptions == [subscribe(200, 590)]
        assert ys.subscriptions == [subscribe(200, 900)]

    def test_window_toggle_on_error(self):
        ex = "ex"
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
            on_completed(590),
        )
        ys = scheduler.create_hot_observable(
            on_next(255, 50),
            on_next(330, 100),
            on_next(350, 50),
            on_next(400, 90),
            on_completed(900),
        )

        def create():
            def closing(x):
                raise Exception(ex)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_toggle(ys, closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [on_error(255, ex)]
        assert xs.subscriptions == [subscribe(200, 255)]
        assert ys.subscriptions == [subscribe(200, 255)]

    def test_window_toggle_dispose(self):
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
            on_completed(590),
        )
        ys = scheduler.create_hot_observable(
            on_next(255, 50),
            on_next(330, 100),
            on_next(350, 50),
            on_next(400, 90),
            on_completed(900),
        )

        def create():
            def closing(x):
                return rx.timer(x)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_toggle(ys, closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create, disposed=415)
        assert results.messages == [
            on_next(260, "0 4"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(410, "3 7"),
        ]
        assert xs.subscriptions == [subscribe(200, 415)]
        assert ys.subscriptions == [subscribe(200, 415)]

    def test_window_toggle_data_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_error(415, ex),
        )
        ys = scheduler.create_hot_observable(
            on_next(255, 50),
            on_next(330, 100),
            on_next(350, 50),
            on_next(400, 90),
            on_completed(900),
        )

        def create():
            def closing(x):
                return rx.timer(x)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_toggle(ys, closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(260, "0 4"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(410, "3 7"),
            on_error(415, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 415)]
        assert ys.subscriptions == [subscribe(200, 415)]

    def test_window_toggle_window_error(self):
        ex = "ex"
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
            on_completed(590),
        )
        ys = scheduler.create_hot_observable(
            on_next(255, 50),
            on_next(330, 100),
            on_next(350, 50),
            on_next(400, 90),
            on_error(415, ex),
        )

        def create():
            def closing(x):
                return rx.timer(x)

            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window_toggle(ys, closing),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(260, "0 4"),
            on_next(340, "1 6"),
            on_next(410, "1 7"),
            on_next(410, "3 7"),
            on_error(415, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 415)]
        assert ys.subscriptions == [subscribe(200, 415)]

    def test_window_simple(self):
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
            on_completed(590),
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_next(400, True),
            on_next(500, True),
            on_completed(900),
        )

        def create():
            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window(ys),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        res = scheduler.start(create=create)

        assert res.messages == [
            on_next(250, "0 3"),
            on_next(260, "1 4"),
            on_next(310, "1 5"),
            on_next(340, "2 6"),
            on_next(410, "4 7"),
            on_next(420, "4 8"),
            on_next(470, "4 9"),
            on_next(550, "5 10"),
            on_completed(590),
        ]

        assert xs.subscriptions == [subscribe(200, 590)]

        assert ys.subscriptions == [subscribe(200, 590)]

    def test_window_close_boundaries(self):
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
            on_completed(590),
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_completed(400),
        )

        def create():
            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window(ys),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        res = scheduler.start(create=create)

        assert res.messages == [
            on_next(250, "0 3"),
            on_next(260, "1 4"),
            on_next(310, "1 5"),
            on_next(340, "2 6"),
            on_completed(400),
        ]

        assert xs.subscriptions == [subscribe(200, 400)]

        assert ys.subscriptions == [subscribe(200, 400)]

    def test_window_throwSource(self):
        ex = "ex"
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(380, 7),
            on_error(400, ex),
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_completed(500),
        )

        def create():
            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window(ys),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        res = scheduler.start(create=create)

        assert res.messages == [
            on_next(250, "0 3"),
            on_next(260, "1 4"),
            on_next(310, "1 5"),
            on_next(340, "2 6"),
            on_next(380, "3 7"),
            on_error(400, ex),
        ]

        assert xs.subscriptions == [subscribe(200, 400)]

        assert ys.subscriptions == [subscribe(200, 400)]

    def test_window_throw_boundaries(self):
        ex = "ex"
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
            on_completed(590),
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_error(400, ex),
        )

        def create():
            def mapper(w, i):
                return w.pipe(ops.map(lambda x: str(i) + " " + str(x)))

            return xs.pipe(
                ops.window(ys),
                ops.map_indexed(mapper),
                ops.merge_all(),
            )

        res = scheduler.start(create=create)

        assert res.messages == [
            on_next(250, "0 3"),
            on_next(260, "1 4"),
            on_next(310, "1 5"),
            on_next(340, "2 6"),
            on_error(400, ex),
        ]

        assert xs.subscriptions == [subscribe(200, 400)]

        assert ys.subscriptions == [subscribe(200, 400)]


if __name__ == "__main__":
    unittest.main()
