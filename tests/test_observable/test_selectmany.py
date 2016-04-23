import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestSelectMany(unittest.TestCase):

    def test_select_many_then_complete_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_completed(250))

        def factory():
            return xs.select_many(ys)

        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_next(600, "qux"), on_next(600, "bar"), on_next(650, "baz"), on_next(650, "foo"), on_next(700, "qux"), on_next(700, "bar"), on_next(750, "baz"), on_next(800, "qux"), on_completed(850))
        xs.subscriptions.assert_equal(subscribe(200, 700))
        ys.subscriptions.assert_equal(subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850))

    def test_select_many_then_complete_complete_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_completed(700))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_completed(250))

        def factory():
            return xs.select_many(ys)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_next(600, "qux"), on_next(600, "bar"), on_next(650, "baz"), on_next(650, "foo"), on_next(700, "qux"), on_next(700, "bar"), on_next(750, "baz"), on_next(800, "qux"), on_completed(900))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        ys.subscriptions.assert_equal(subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850))

    def test_select_many_then_never_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_next(500, 5), on_next(700, 0))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_completed(250))
        results = scheduler.start(lambda: xs.select_many(ys))

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_next(600, "qux"), on_next(600, "bar"), on_next(650, "baz"), on_next(650, "foo"), on_next(700, "qux"), on_next(700, "bar"), on_next(750, "baz"), on_next(750, "foo"), on_next(800, "qux"), on_next(800, "bar"), on_next(850, "baz"), on_next(900, "qux"), on_next(950, "foo"))
        xs.subscriptions.assert_equal(subscribe(200, 1000))
        ys.subscriptions.assert_equal(subscribe(300, 550), subscribe(400, 650), subscribe(500, 750), subscribe(600, 850), subscribe(700, 950), subscribe(900, 1000))

    def test_select_many_then_complete_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"))
        results = scheduler.start(lambda: xs.select_many(ys))

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_next(600, "qux"), on_next(600, "bar"), on_next(650, "baz"), on_next(650, "foo"), on_next(700, "qux"), on_next(700, "bar"), on_next(750, "baz"), on_next(800, "qux"))
        xs.subscriptions.assert_equal(subscribe(200, 700))
        ys.subscriptions.assert_equal(subscribe(300, 1000), subscribe(400, 1000), subscribe(500, 1000), subscribe(600, 1000))

    def test_select_many_then_complete_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_error(300, ex))
        results = scheduler.start(lambda: xs.select_many(ys))

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_error(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        ys.subscriptions.assert_equal(subscribe(300, 600), subscribe(400, 600), subscribe(500, 600), subscribe(600, 600))

    def test_select_many_then_error_complete(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_error(500, ex))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_completed(250))
        results = scheduler.start(lambda: xs.select_many(ys))

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_next(550, "baz"), on_next(550, "foo"), on_next(600, "qux"), on_next(600, "bar"), on_next(650, "baz"), on_next(650, "foo"), on_error(700, ex))
        xs.subscriptions.assert_equal(subscribe(200, 700))
        ys.subscriptions.assert_equal(subscribe(300, 550), subscribe(400, 650), subscribe(500, 700), subscribe(600, 700))

    def test_select_many_then_error_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 4), on_next(200, 2), on_next(300, 3), on_next(400, 1), on_error(500, ex))
        ys = scheduler.create_cold_observable(on_next(50, "foo"), on_next(100, "bar"), on_next(150, "baz"), on_next(200, "qux"), on_error(250, ex))
        results = scheduler.start(lambda: xs.select_many(ys))

        results.messages.assert_equal(on_next(350, "foo"), on_next(400, "bar"), on_next(450, "baz"), on_next(450, "foo"), on_next(500, "qux"), on_next(500, "bar"), on_error(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))
        ys.subscriptions.assert_equal(subscribe(300, 550), subscribe(400, 550), subscribe(500, 550))


    def test_select_many_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_completed(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303), on_next(740, 106), on_next(810, 304), on_next(860, 305), on_next(930, 401), on_next(940, 402), on_completed(960))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 760))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 605))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 960))
        xs.messages[5].value.value.subscriptions.assert_equal(subscribe(750, 790))
        xs.messages[6].value.value.subscriptions.assert_equal(subscribe(850, 950))

    def test_select_many_complete_inner_not_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_completed(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303), on_next(740, 106), on_next(810, 304), on_next(860, 305), on_next(930, 401), on_next(940, 402))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 760))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 1000))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 960))
        xs.messages[5].value.value.subscriptions.assert_equal(subscribe(750, 790))
        xs.messages[6].value.value.subscriptions.assert_equal(subscribe(850, 950))

    def test_select_many_complete_outer_not_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303), on_next(740, 106), on_next(810, 304), on_next(860, 305), on_next(930, 401), on_next(940, 402))
        xs.subscriptions.assert_equal(subscribe(200, 1000))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 760))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 605))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 960))
        xs.messages[5].value.value.subscriptions.assert_equal(subscribe(750, 790))
        xs.messages[6].value.value.subscriptions.assert_equal(subscribe(850, 950))

    def test_select_many_error_outer(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_error(900, ex))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303), on_next(740, 106), on_next(810, 304), on_next(860, 305), on_error(900, ex))
        xs.subscriptions.assert_equal(subscribe(200, 900))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 760))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 605))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 900))
        xs.messages[5].value.value.subscriptions.assert_equal(subscribe(750, 790))
        xs.messages[6].value.value.subscriptions.assert_equal(subscribe(850, 900))

    def test_select_many_error_inner(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_error(460, ex))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_completed(900))

        def factory():
            return xs.select_many(lambda x: x)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303), on_next(740, 106), on_error(760, ex))
        xs.subscriptions.assert_equal(subscribe(200, 760))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 760))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 605))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 760))
        xs.messages[5].value.value.subscriptions.assert_equal(subscribe(750, 760))
        xs.messages[6].value.value.subscriptions.assert_equal()

    def test_select_many_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_completed(900))

        def create():
            return xs.select_many(lambda x: x)
        results = scheduler.start(create, disposed=700)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_next(560, 301), on_next(580, 202), on_next(590, 203), on_next(600, 302), on_next(620, 303))
        xs.subscriptions.assert_equal(subscribe(200, 700))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 700))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 605))
        xs.messages[4].value.value.subscriptions.assert_equal(subscribe(550, 700))
        xs.messages[5].value.value.subscriptions.assert_equal()
        xs.messages[6].value.value.subscriptions.assert_equal()

    def test_select_many_throw(self):
        invoked = [0]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(5, scheduler.create_cold_observable(on_error(1, 'ex1'))), on_next(105, scheduler.create_cold_observable(on_error(1, 'ex2'))), on_next(300, scheduler.create_cold_observable(on_next(10, 102), on_next(90, 103), on_next(110, 104), on_next(190, 105), on_next(440, 106), on_completed(460))), on_next(400, scheduler.create_cold_observable(on_next(180, 202), on_next(190, 203), on_completed(205))), on_next(550, scheduler.create_cold_observable(on_next(10, 301), on_next(50, 302), on_next(70, 303), on_next(260, 304), on_next(310, 305), on_completed(410))), on_next(750, scheduler.create_cold_observable(on_completed(40))), on_next(850, scheduler.create_cold_observable(on_next(80, 401), on_next(90, 402), on_completed(100))), on_completed(900))

        def factory():
            def projection(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)
                return x
            return xs.select_many(projection)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(310, 102), on_next(390, 103), on_next(410, 104), on_next(490, 105), on_error(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))
        xs.messages[2].value.value.subscriptions.assert_equal(subscribe(300, 550))
        xs.messages[3].value.value.subscriptions.assert_equal(subscribe(400, 550))
        xs.messages[4].value.value.subscriptions.assert_equal()
        xs.messages[5].value.value.subscriptions.assert_equal()
        xs.messages[6].value.value.subscriptions.assert_equal()

    def test_select_many_use_function(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 4), on_next(220, 3), on_next(250, 5), on_next(270, 1), on_completed(290))

        def factory():
            def projection(x):
                return Observable.interval(10, scheduler).map(lambda a, b: x).take(x)
            return xs.select_many(projection)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(220, 4), on_next(230, 3), on_next(230, 4), on_next(240, 3), on_next(240, 4), on_next(250, 3), on_next(250, 4), on_next(260, 5), on_next(270, 5), on_next(280, 1), on_next(280, 5), on_next(290, 5), on_next(300, 5), on_completed(300))
        xs.subscriptions.assert_equal(subscribe(200, 290))

    def test_flat_map_iterable_complete(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(340, 4),
            on_next(420, 3),
            on_next(510, 2),
            on_completed(600)
        )
        inners = []

        def create():
            def mapper(x):
                ys = [x] * x
                inners.append(ys)
                return ys
            return xs.flat_map(mapper)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(210, 2),
            on_next(210, 2),
            on_next(340, 4),
            on_next(340, 4),
            on_next(340, 4),
            on_next(340, 4),
            on_next(420, 3),
            on_next(420, 3),
            on_next(420, 3),
            on_next(510, 2),
            on_next(510, 2),
            on_completed(600)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 600)
        )
        assert(4 == len(inners))

    def test_flat_map_iterable_complete_result_selector(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(340, 4),
            on_next(420, 3),
            on_next(510, 2),
            on_completed(600)
        )

        def create():
            return xs.flat_map(lambda x, i: [x] * x, lambda x,y, i: x + y)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(210, 4),
            on_next(210, 4),
            on_next(340, 8),
            on_next(340, 8),
            on_next(340, 8),
            on_next(340, 8),
            on_next(420, 6),
            on_next(420, 6),
            on_next(420, 6),
            on_next(510, 4),
            on_next(510, 4),
            on_completed(600)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 600)
        )

if __name__ == '__main__':
    unittest.main()
