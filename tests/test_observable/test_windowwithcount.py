import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowWithCount(unittest.TestCase):
    def test_window_with_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), close(600))
        def create():
            def proj(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window_with_count(3, 2).map_indexed(proj).merge_all()
        results = scheduler.start(create)

        assert results.messages == [send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6"), send(380, "2 7"), send(420, "2 8"), send(420, "3 8"), send(470, "3 9"), close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_window_with_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), close(600))

        def create():
            def proj(w, i):
                return w.map(lambda x: str(i) + ' ' + str(x))
            return xs.window_with_count(3, 2).map_indexed(proj).merge_all()

        results = scheduler.start(create, disposed=370)
        assert results.messages == [send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6")]
        assert xs.subscriptions == [subscribe(200, 370)]

    def test_window_with_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(380, 7), send(420, 8), send(470, 9), throw(600, ex))

        def create():
            def selector(w, i):
                def mapping(x):
                    return "%s %s" % (i, x)
                return w.map(mapping)
            return xs.window_with_count(3, 2).map_indexed(selector).merge_all()

        results = scheduler.start(create)

        assert results.messages == [send(210, "0 2"), send(240, "0 3"), send(280, "0 4"), send(280, "1 4"), send(320, "1 5"), send(350, "1 6"), send(350, "2 6"), send(380, "2 7"), send(420, "2 8"), send(420, "3 8"), send(470, "3 9"), throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
