import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestSelectMany(unittest.TestCase):

    def test_select_many_then_complete_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), close(500))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), close(250))

        def factory():
            return xs.select_many(ys)

        results = scheduler.start(factory)

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), send(600, "qux"), send(600, "bar"), send(650, "baz"), send(650, "foo"), send(700, "qux"), send(700, "bar"), send(750, "baz"), send(800, "qux"), close(850)]
        assert xs.subscriptions == [subscribe(200, 700)]
        assert ys.subscriptions == [subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850)]

    def test_select_many_then_complete_complete_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), close(700))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), close(250))

        def factory():
            return xs.select_many(ys)
        results = scheduler.start(factory)

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), send(600, "qux"), send(600, "bar"), send(650, "baz"), send(650, "foo"), send(700, "qux"), send(700, "bar"), send(750, "baz"), send(800, "qux"), close(900)]
        assert xs.subscriptions == [subscribe(200, 900)]
        assert ys.subscriptions == [subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850)]

    def test_select_many_then_never_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), send(500, 5), send(700, 0))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), close(250))
        results = scheduler.start(lambda: xs.select_many(ys))

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), send(600, "qux"), send(600, "bar"), send(650, "baz"), send(650, "foo"), send(700, "qux"), send(700, "bar"), send(750, "baz"), send(750, "foo"), send(800, "qux"), send(800, "bar"), send(850, "baz"), send(900, "qux"), send(950, "foo")]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert ys.subscriptions == [subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850), subscribe(700, 950), subscribe(900, 1000)]

    def test_select_many_then_complete_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), close(500))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"))
        results = scheduler.start(lambda: xs.select_many(ys))

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), send(600, "qux"), send(600, "bar"), send(650, "baz"), send(650, "foo"), send(700, "qux"), send(700, "bar"), send(750, "baz"), send(800, "qux")]
        assert xs.subscriptions == [subscribe(200, 700)]
        assert ys.subscriptions == [subscribe(300, 1000), subscribe(400, 1000), subscribe(500, 1000), subscribe(600, 1000)]

    def test_select_many_then_complete_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), close(500))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), throw(300, ex))
        results = scheduler.start(lambda: xs.select_many(ys))

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert ys.subscriptions == [subscribe(300, 600), subscribe(400, 600), subscribe(500, 600), subscribe(600, 600)]

    def test_select_many_then_error_complete(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), throw(500, ex))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), close(250))
        results = scheduler.start(lambda: xs.select_many(ys))

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), send(550, "baz"), send(550, "foo"), send(600, "qux"), send(600, "bar"), send(650, "baz"), send(650, "foo"), throw(700, ex)]
        assert xs.subscriptions == [subscribe(200, 700)]
        assert ys.subscriptions == [subscribe(300, 550), subscribe(400, 650), subscribe(500, 700), subscribe(600, 700)]

    def test_select_many_then_error_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 4), send(200, 2), send(300, 3), send(400, 1), throw(500, ex))
        ys = scheduler.create_cold_observable(send(50, "foo"), send(100, "bar"), send(150, "baz"), send(200, "qux"), throw(250, ex))
        results = scheduler.start(lambda: xs.select_many(ys))

        assert results.messages == [send(350, "foo"), send(400, "bar"), send(450, "baz"), send(450, "foo"), send(500, "qux"), send(500, "bar"), throw(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert ys.subscriptions == [subscribe(300, 550), subscribe(400, 550), subscribe(500, 550)]


    def test_select_many_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), close(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303), send(740, 106), send(810, 304), send(860, 305), send(930, 401), send(940, 402), close(960)]
        assert xs.subscriptions == [subscribe(200, 900)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 760)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 605)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 960)]
        assert xs.messages[5].value.value.subscriptions == [subscribe(750, 790)]
        assert xs.messages[6].value.value.subscriptions == [subscribe(850, 950)]

    def test_select_many_complete_inner_not_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), close(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303), send(740, 106), send(810, 304), send(860, 305), send(930, 401), send(940, 402)]
        assert xs.subscriptions == [subscribe(200, 900)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 760)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 1000)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 960)]
        assert xs.messages[5].value.value.subscriptions == [subscribe(750, 790)]
        assert xs.messages[6].value.value.subscriptions == [subscribe(850, 950)]

    def test_select_many_complete_outer_not_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303), send(740, 106), send(810, 304), send(860, 305), send(930, 401), send(940, 402)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 760)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 605)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 960)]
        assert xs.messages[5].value.value.subscriptions == [subscribe(750, 790)]
        assert xs.messages[6].value.value.subscriptions == [subscribe(850, 950)]

    def test_select_many_error_outer(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), throw(900, ex))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303), send(740, 106), send(810, 304), send(860, 305), throw(900, ex)]
        assert xs.subscriptions == [subscribe(200, 900)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 760)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 605)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 900)]
        assert xs.messages[5].value.value.subscriptions == [subscribe(750, 790)]
        assert xs.messages[6].value.value.subscriptions == [subscribe(850, 900)]

    def test_select_many_error_inner(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), throw(460, ex))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), close(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303), send(740, 106), throw(760, ex)]
        assert xs.subscriptions == [subscribe(200, 760)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 760)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 605)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 760)]
        assert xs.messages[5].value.value.subscriptions == [subscribe(750, 760)]
        assert xs.messages[6].value.value.subscriptions == []

    def test_select_many_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), close(900))

        def create():
            return xs.select_many(lambda x: x)
        results = scheduler.start(create, disposed=700)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), send(560, 301), send(580, 202), send(590, 203), send(600, 302), send(620, 303)]
        assert xs.subscriptions == [subscribe(200, 700)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 700)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 605)]
        assert xs.messages[4].value.value.subscriptions == [subscribe(550, 700)]
        assert xs.messages[5].value.value.subscriptions == []
        assert xs.messages[6].value.value.subscriptions == []

    def test_select_many_throw(self):
        invoked = [0]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(5, scheduler.create_cold_observable(throw(1, 'ex1'))), send(105, scheduler.create_cold_observable(throw(1, 'ex2'))), send(300, scheduler.create_cold_observable(send(10, 102), send(90, 103), send(110, 104), send(190, 105), send(440, 106), close(460))), send(400, scheduler.create_cold_observable(send(180, 202), send(190, 203), close(205))), send(550, scheduler.create_cold_observable(send(10, 301), send(50, 302), send(70, 303), send(260, 304), send(310, 305), close(410))), send(750, scheduler.create_cold_observable(close(40))), send(850, scheduler.create_cold_observable(send(80, 401), send(90, 402), close(100))), close(900))

        def factory():
            def projection(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)
                return x
            return xs.select_many(projection)
        results = scheduler.start(factory)

        assert results.messages == [send(310, 102), send(390, 103), send(410, 104), send(490, 105), throw(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]
        assert xs.messages[2].value.value.subscriptions == [subscribe(300, 550)]
        assert xs.messages[3].value.value.subscriptions == [subscribe(400, 550)]
        assert xs.messages[4].value.value.subscriptions == []
        assert xs.messages[5].value.value.subscriptions == []
        assert xs.messages[6].value.value.subscriptions == []

    def test_select_many_use_function(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 4), send(220, 3), send(250, 5), send(270, 1), close(290))

        def factory():
            def projection(x):
                return Observable.interval(10).map_indexed(lambda a, b: x).take(x)
            return xs.select_many(projection)
        results = scheduler.start(factory)

        assert results.messages == [send(220, 4), send(230, 3), send(230, 4), send(240, 3), send(240, 4), send(250, 3), send(250, 4), send(260, 5), send(270, 5), send(280, 1), send(280, 5), send(290, 5), send(300, 5), close(300)]
        assert xs.subscriptions == [subscribe(200, 290)]

    def test_flat_map_iterable_complete(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(210, 2),
            send(340, 4),
            send(420, 3),
            send(510, 2),
            close(600)
        )
        inners = []

        def create():
            def mapper(x):
                ys = [x] * x
                inners.append(ys)
                return ys
            return xs.flat_map(mapper)
        res = scheduler.start(create)

        assert res.messages == [
            send(210, 2),
            send(210, 2),
            send(340, 4),
            send(340, 4),
            send(340, 4),
            send(340, 4),
            send(420, 3),
            send(420, 3),
            send(420, 3),
            send(510, 2),
            send(510, 2),
            close(600)]

        assert xs.subscriptions == [
            subscribe(200, 600)]
        assert(4 == len(inners))

    def test_flat_map_iterable_complete_result_selector(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(210, 2),
            send(340, 4),
            send(420, 3),
            send(510, 2),
            close(600)
        )

        def create():
            return xs.flat_map(lambda x, i: [x] * x, lambda x,y, i: x + y)

        res = scheduler.start(create)

        assert res.messages == [
            send(210, 4),
            send(210, 4),
            send(340, 8),
            send(340, 8),
            send(340, 8),
            send(340, 8),
            send(420, 6),
            send(420, 6),
            send(420, 6),
            send(510, 4),
            send(510, 4),
            close(600)]

        assert xs.subscriptions == [subscribe(200, 600)]

if __name__ == '__main__':
    unittest.main()
