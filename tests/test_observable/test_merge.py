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


class TestMerge(unittest.TestCase):
    def test_merge_never2(self):
        scheduler = TestScheduler()
        n1 = Observable.never()
        n2 = Observable.never()

        def create():
            return Observable.merge(n1, n2)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_merge_never3(self):
        scheduler = TestScheduler()
        n1 = Observable.never()
        n2 = Observable.never()
        n3 = Observable.never()

        def create():
            return Observable.merge(n1, n2, n3)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_merge_empty2(self):
        scheduler = TestScheduler()
        e1 = Observable.empty()
        e2 = Observable.empty()

        def create():
            return Observable.merge(e1, e2)

        results = scheduler.start(create)
        results.messages.assert_equal(close(203))

    def test_merge_empty3(self):
        scheduler = TestScheduler()
        e1 = Observable.empty()
        e2 = Observable.empty()
        e3 = Observable.empty()

        def create():
            return Observable.merge(e1, e2, e3)

        results = scheduler.start(create)
        results.messages.assert_equal(close(204))

    def test_merge_empty_delayed2_right_last(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), close(240)]
        r_msgs = [send(150, 1), close(250)]
        e1 = scheduler.create_hot_observable(l_msgs)
        e2 = scheduler.create_hot_observable(r_msgs)

        def create():
            return Observable.merge(e1, e2)

        results = scheduler.start(create)
        results.messages.assert_equal(close(250))

    def test_merge_empty_delayed2_left_last(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), close(250)]
        r_msgs = [send(150, 1), close(240)]
        e1 = scheduler.create_hot_observable(l_msgs)
        e2 = scheduler.create_hot_observable(r_msgs)

        def create():
            return Observable.merge(e1, e2)
        results = scheduler.start(create)
        results.messages.assert_equal(close(250))

    def test_merge_empty_delayed3_middle_last(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(245)]
        msgs2 = [send(150, 1), close(250)]
        msgs3 = [send(150, 1), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)
        e3 = scheduler.create_hot_observable(msgs3)

        def create():
           return Observable.merge(e1, e2, e3)

        results = scheduler.start(create)
        results.messages.assert_equal(close(250))

    def test_merge_empty_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(245)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
           return Observable.merge(e1, n1)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_merge_never_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(245)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
            return Observable.merge(n1, e1)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_merge_return_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(245)]
        r1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
            return Observable.merge(r1, n1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2))

    def test_merge_never_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(245)]
        r1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
            return Observable.merge(n1, r1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2))

    def test_merge_error_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
            return Observable.merge(e1, n1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), throw(245, ex))

    def test_merge_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = Observable.never()

        def create():
            return Observable.merge(n1, e1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), throw(245, ex))

    def test_merge_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(245)]
        msgs2 = [send(150, 1), send(210, 2), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        r1 = scheduler.create_hot_observable(msgs2)

        def create():
            return Observable.merge(e1, r1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), close(250))

    def test_merge_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(245)]
        msgs2 = [send(150, 1), send(210, 2), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        r1 = scheduler.create_hot_observable(msgs2)

        def create():
            return Observable.merge(r1, e1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), close(250))

    def test_merge_lots2(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 4), send(230, 6), send(240, 8), close(245)]
        msgs2 = [send(150, 1), send(215, 3), send(225, 5), send(235, 7), send(245, 9), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return Observable.merge(o1, o2)

        results = scheduler.start(create).messages
        assert(len(results) == 9)
        for i, result in enumerate(results[:-1]):
            assert(result.value.kind == 'N')
            assert(result.time == 210 + i * 5)
            assert(result.value.value == i + 2)

        assert(results[8].value.kind == 'C' and results[8].time == 250)

    def test_merge_lots3(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(225, 5), send(240, 8), close(245)]
        msgs2 = [send(150, 1), send(215, 3), send(230, 6), send(245, 9), close(250)]
        msgs3 = [send(150, 1), send(220, 4), send(235, 7), close(240)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            return Observable.merge(o1, o2, o3)

        results = scheduler.start(create).messages
        assert(len(results) == 9)
        for i, result in enumerate(results[:-1]):
            assert(results[i].value.kind == 'N' and results[i].time == 210 + i * 5 and results[i].value.value == i + 2)

        assert(results[8].value.kind == 'C' and results[8].time == 250)

    def test_merge_error_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(245, ex)]
        msgs2 = [send(150, 1), send(215, 3), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return Observable.merge(o1, o2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), send(215, 3), throw(245, ex))

    def test_merge_error_causes_disposal(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(210, ex)]
        msgs2 = [send(150, 1), send(220, 1), close(250)]
        source_not_disposed = [False]
        o1 = scheduler.create_hot_observable(msgs1)

        def action():
            source_not_disposed[0] = True

        o2 = scheduler.create_hot_observable(msgs2).do_action(send=action)

        def create():
            return Observable.merge(o1, o2)

        results = scheduler.start(create)

        results.messages.assert_equal(throw(210, ex))
        assert(not source_not_disposed[0])

    def test_merge_observable_of_observable_data(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), send(110, 103), send(120, 104), send(210, 105), send(220, 106), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), close(50))), send(500, scheduler.create_cold_observable(send(10, 301), send(20, 302), send(30, 303), send(40, 304), send(120, 305), close(150))), close(600))

        def create():
            return xs.merge_observable()
        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 103), send(410, 201), send(420, 104), send(420, 202), send(430, 203), send(440, 204), send(510, 105), send(510, 301), send(520, 106), send(520, 302), send(530, 303), send(540, 304), send(620, 305), close(650))

    def test_merge_observable_of_observable_data_non_overlapped(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), close(50))), send(500, scheduler.create_cold_observable(send(10, 301), send(20, 302), send(30, 303), send(40, 304), close(50))), close(600))

        def create():
            return xs.merge_observable()

        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), send(510, 301), send(520, 302), send(530, 303), send(540, 304), close(600))

    def test_merge_observable_of_observable_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), throw(50, ex))), send(500, scheduler.create_cold_observable(send(10, 301), send(20, 302), send(30, 303), send(40, 304), close(50))), close(600))

        def create():
            return xs.merge_observable()

        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), throw(450, ex))

    def test_merge_observable_of_observable_outer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), close(50))), throw(500, ex))

        def create():
            return xs.merge_observable()
        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), throw(500, ex))

    def test_mergeconcat_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(200))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(320, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(400))

        def create():
            return xs.merge(2)

        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(310, 2), send(330, 3), send(330, 5), send(360, 6), send(440, 7), send(460, 8), send(670, 9), send(700, 10), close(760))
        xs.subscriptions.assert_equal(subscribe(200, 760))

    def test_mergeconcat_basic_long(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(300))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(320, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(400))

        def create():
            return xs.merge(2)

        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(310, 2), send(330, 3), send(330, 5), send(360, 6), send(440, 7), send(460, 8), send(690, 9), send(720, 10), close(780))
        xs.subscriptions.assert_equal(subscribe(200, 780))

    def test_mergeconcat_basic_wide(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(300))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(420, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(450))

        def create():
            return xs.merge(3)

        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(280, 6), send(310, 2), send(330, 3), send(330, 5), send(360, 7), send(380, 8), send(630, 9), send(660, 10), close(720))
        xs.subscriptions.assert_equal(subscribe(200, 720))

    def test_mergeconcat_basic_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(300))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(420, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(750))

        def create():
            return xs.merge(3)

        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(280, 6), send(310, 2), send(330, 3), send(330, 5), send(360, 7), send(380, 8), send(630, 9), send(660, 10), close(750))
        xs.subscriptions.assert_equal(subscribe(200, 750))

    def test_mergeconcat_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(200))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(320, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(400))

        def create():
            return xs.merge(2)

        results = scheduler.start(create, disposed=450)
        results.messages.assert_equal(send(260, 1), send(280, 4), send(310, 2), send(330, 3), send(330, 5), send(360, 6), send(440, 7))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_mergeconcat_outererror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(200))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), close(130))), send(320, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), throw(400, ex))

        def create():
            return xs.merge(2)
        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(310, 2), send(330, 3), send(330, 5), send(360, 6), throw(400, ex))
        xs.subscriptions.assert_equal(subscribe(200, 400))

    def test_mergeconcat_innererror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, scheduler.create_cold_observable(send(50, 1), send(100, 2), send(120, 3), close(140))), send(260, scheduler.create_cold_observable(send(20, 4), send(70, 5), close(200))), send(270, scheduler.create_cold_observable(send(10, 6), send(90, 7), send(110, 8), throw(140, ex))), send(320, scheduler.create_cold_observable(send(210, 9), send(240, 10), close(300))), close(400))

        def create():
            return xs.merge(2)

        results = scheduler.start(create)

        results.messages.assert_equal(send(260, 1), send(280, 4), send(310, 2), send(330, 3), send(330, 5), send(360, 6), send(440, 7), send(460, 8), throw(490, ex))
        xs.subscriptions.assert_equal(subscribe(200, 490))

    def test_merge_112233(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(250, 1), send(300, 2), send(350, 3), close(360))
        ys = scheduler.create_hot_observable(
            send(250, 1), send(300, 2), send(320, 3), close(340))

        def create():
            return xs.merge(ys)

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(250, 1),
            send(250, 1),
            send(300, 2),
            send(300, 2),
            send(320, 3),
            send(350, 3),
            close(360))
        xs.subscriptions.assert_equal(subscribe(202, 360))
