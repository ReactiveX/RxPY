import unittest
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithTime(unittest.TestCase):
    def test_window_with_time_or_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), close(600))

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return "%s %s" % (i, x)
                return w.map(inner_proj)
            return xs.window_with_time_or_count(70, 3).map_indexed(projection).merge_observable()

        results = scheduler.start(create)
        assert results.messages == [send(205, "0 1"), send(210, "0 2"), send(240, "0 3"), send(280, "1 4"), send(320, "2 5"), send(350, "2 6"), send(370, "2 7"), send(420, "3 8"), send(470, "4 9"), close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_window_with_time_or_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), throw(600, ex))

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return "%s %s" % (i, x)
                return w.map(inner_proj)
            return xs.window_with_time_or_count(70, 3).map_indexed(projection).merge_observable()

        results = scheduler.start(create)

        assert results.messages == [send(205, "0 1"), send(210, "0 2"), send(240, "0 3"), send(280, "1 4"), send(320, "2 5"), send(350, "2 6"), send(370, "2 7"), send(420, "3 8"), send(470, "4 9"), throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_window_with_time_or_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), close(600))

        def create():
            def projection(w, i):
                def inner_proj(x):
                    return "%s %s" % (i, x)
                return w.map(inner_proj)
            return xs.window_with_time_or_count(70, 3).map_indexed(projection).merge_observable()

        results = scheduler.start(create, disposed=370)
        assert results.messages == [send(205, "0 1"), send(210, "0 2"), send(240, "0 3"), send(280, "1 4"), send(320, "2 5"), send(350, "2 6"), send(370, "2 7")]
        assert xs.subscriptions == [subscribe(200, 370)]



