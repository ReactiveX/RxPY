import unittest

import pytest

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


class TestMerge(unittest.TestCase):
    def test_merge_never2(self):
        scheduler = TestScheduler()
        n1 = rx.never()
        n2 = rx.never()

        def create():
            return rx.merge(n1, n2)

        results = scheduler.start(create)
        assert results.messages == []

    def test_merge_never3(self):
        scheduler = TestScheduler()
        n1 = rx.never()
        n2 = rx.never()
        n3 = rx.never()

        def create():
            return rx.merge(n1, n2, n3)

        results = scheduler.start(create)
        assert results.messages == []

    def test_merge_empty2(self):
        scheduler = TestScheduler()
        e1 = rx.empty()
        e2 = rx.empty()

        def create():
            return rx.merge(e1, e2)

        results = scheduler.start(create)
        assert results.messages == [on_completed(200)]

    def test_merge_empty3(self):
        scheduler = TestScheduler()
        e1 = rx.empty()
        e2 = rx.empty()
        e3 = rx.empty()

        def create():
            return rx.merge(e1, e2, e3)

        results = scheduler.start(create)
        assert results.messages == [on_completed(200)]

    def test_merge_empty_delayed2_right_last(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_completed(240)]
        r_msgs = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(l_msgs)
        e2 = scheduler.create_hot_observable(r_msgs)

        def create():
            return rx.merge(e1, e2)

        results = scheduler.start(create)
        assert results.messages == [on_completed(250)]

    def test_merge_empty_delayed2_left_last(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_completed(250)]
        r_msgs = [on_next(150, 1), on_completed(240)]
        e1 = scheduler.create_hot_observable(l_msgs)
        e2 = scheduler.create_hot_observable(r_msgs)

        def create():
            return rx.merge(e1, e2)
        results = scheduler.start(create)
        assert results.messages == [on_completed(250)]

    def test_merge_empty_delayed3_middle_last(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(245)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        msgs3 = [on_next(150, 1), on_completed(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)
        e3 = scheduler.create_hot_observable(msgs3)

        def create():
            return rx.merge(e1, e2, e3)

        results = scheduler.start(create)
        assert results.messages == [on_completed(250)]

    def test_merge_empty_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(245)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(e1, n1)

        results = scheduler.start(create)
        assert results.messages == []

    def test_merge_never_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(245)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(n1, e1)

        results = scheduler.start(create)
        assert results.messages == []

    def test_merge_return_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
        r1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(r1, n1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2)]

    def test_merge_never_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
        r1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(n1, r1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2)]

    def test_merge_error_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(e1, n1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_error(245, ex)]

    def test_merge_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        n1 = rx.never()

        def create():
            return rx.merge(n1, e1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_error(245, ex)]

    def test_merge_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(245)]
        msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        r1 = scheduler.create_hot_observable(msgs2)

        def create():
            return rx.merge(e1, r1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_completed(250)]

    def test_merge_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(245)]
        msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        r1 = scheduler.create_hot_observable(msgs2)

        def create():
            return rx.merge(r1, e1)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_completed(250)]

    def test_merge_lots2(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 6), on_next(240, 8), on_completed(245)]
        msgs2 = [on_next(150, 1), on_next(215, 3), on_next(225, 5), on_next(235, 7), on_next(245, 9), on_completed(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return rx.merge(o1, o2)

        results = scheduler.start(create).messages
        assert(len(results) == 9)
        for i, result in enumerate(results[:-1]):
            assert(result.value.kind == 'N')
            assert(result.time == 210 + i * 5)
            assert(result.value.value == i + 2)

        assert(results[8].value.kind == 'C' and results[8].time == 250)

    def test_merge_lots3(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(225, 5), on_next(240, 8), on_completed(245)]
        msgs2 = [on_next(150, 1), on_next(215, 3), on_next(230, 6), on_next(245, 9), on_completed(250)]
        msgs3 = [on_next(150, 1), on_next(220, 4), on_next(235, 7), on_completed(240)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            return rx.merge(o1, o2, o3)

        results = scheduler.start(create).messages
        assert(len(results) == 9)
        for i, result in enumerate(results[:-1]):
            assert(results[i].value.kind == 'N' and results[i].time == 210 + i * 5 and results[i].value.value == i + 2)

        assert(results[8].value.kind == 'C' and results[8].time == 250)

    def test_merge_error_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
        msgs2 = [on_next(150, 1), on_next(215, 3), on_completed(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return rx.merge(o1, o2)

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_next(215, 3), on_error(245, ex)]

    def test_merge_error_causes_disposal(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(210, ex)]
        msgs2 = [on_next(150, 1), on_next(220, 1), on_completed(250)]
        source_not_disposed = [False]
        o1 = scheduler.create_hot_observable(msgs1)

        def action():
            source_not_disposed[0] = True

        o2 = scheduler.create_hot_observable(msgs2).pipe(ops.do_action(on_next=action))

        def create():
            return rx.merge(o1, o2)

        results = scheduler.start(create)

        assert results.messages == [on_error(210, ex)]
        assert(not source_not_disposed[0])

    def test_merge_observable_of_observable_data(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(
            on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 200), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_next(120, 305), on_completed(150))), on_completed(600))

        def create():
            return xs.pipe(ops.merge_all())
        results = scheduler.start(create)
        assert results.messages == [on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(410, 201), on_next(420, 104), on_next(420, 202), on_next(430, 203), on_next(
            440, 200), on_next(510, 105), on_next(510, 301), on_next(520, 106), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_next(620, 305), on_completed(650)]

    def test_merge_observable_of_observable_data_non_overlapped(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(
            20, 202), on_next(30, 203), on_next(40, 200), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))

        def create():
            return xs.pipe(ops.merge_all())

        results = scheduler.start(create)
        assert results.messages == [on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(
            430, 203), on_next(440, 200), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(600)]

    def test_merge_observable_of_observable_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(
            20, 202), on_next(30, 203), on_next(40, 200), on_error(50, ex))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))

        def create():
            return xs.pipe(ops.merge_all())

        results = scheduler.start(create)
        assert results.messages == [on_next(310, 101), on_next(320, 102), on_next(
            410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 200), on_error(450, ex)]

    def test_merge_observable_of_observable_outer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(
            400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 200), on_completed(50))), on_error(500, ex))

        def create():
            return xs.pipe(ops.merge_all())
        results = scheduler.start(create)
        assert results.messages == [on_next(310, 101), on_next(320, 102), on_next(
            410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 200), on_error(500, ex)]

    def test_mergeconcat_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, scheduler.create_cold_observable(
                on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))),
            on_next(260, scheduler.create_cold_observable(
                on_next(20, 4), on_next(70, 5), on_completed(200))),
            on_next(270, scheduler.create_cold_observable(
                on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))),
            on_next(320, scheduler.create_cold_observable(
                on_next(210, 9), on_next(240, 10), on_completed(300))),
            on_completed(400))

        def create():
            return xs.pipe(ops.merge(max_concurrent=2))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3),
            on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8),
            on_next(670, 9), on_next(700, 10), on_completed(760)]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_mergeconcat_basic_long(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, scheduler.create_cold_observable(
                on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))),
            on_next(260, scheduler.create_cold_observable(
                on_next(20, 4), on_next(70, 5), on_completed(300))),
            on_next(270, scheduler.create_cold_observable(
                on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))),
            on_next(320, scheduler.create_cold_observable(
                on_next(210, 9), on_next(240, 10), on_completed(300))),
            on_completed(400))

        def create():
            return xs.pipe(ops.merge(max_concurrent=2))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(260, 1), on_next(280, 4), on_next(310, 2),
            on_next(330, 3), on_next(330, 5), on_next(360, 6),
            on_next(440, 7), on_next(460, 8), on_next(690, 9),
            on_next(720, 10), on_completed(780)]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_mergeconcat_basic_wide(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, scheduler.create_cold_observable(
                on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))),
            on_next(260, scheduler.create_cold_observable(
                on_next(20, 4), on_next(70, 5), on_completed(300))),
            on_next(270, scheduler.create_cold_observable(
                on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))),
            on_next(420, scheduler.create_cold_observable(
                on_next(210, 9), on_next(240, 10), on_completed(300))),
            on_completed(450))

        def create():
            return xs.pipe(ops.merge(max_concurrent=3))

        results = scheduler.start(create)

        assert results.messages == [on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(
            330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(720)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_mergeconcat_basic_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(
            300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(750))

        def create():
            return xs.pipe(ops.merge(max_concurrent=3))

        results = scheduler.start(create)

        assert results.messages == [on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(
            330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(750)]
        assert xs.subscriptions == [subscribe(200, 750)]

    def test_mergeconcat_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, scheduler.create_cold_observable(
                on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))),
            on_next(260, scheduler.create_cold_observable(
                on_next(20, 4), on_next(70, 5), on_completed(200))),
            on_next(270, scheduler.create_cold_observable(
                on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))),
            on_next(320, scheduler.create_cold_observable(
                on_next(210, 9), on_next(240, 10), on_completed(300))),
            on_completed(400)
            )

        def create():
            return xs.pipe(ops.merge(max_concurrent=2))

        results = scheduler.start(create, disposed=450)
        assert results.messages == [
            on_next(260, 1), on_next(280, 4), on_next(310, 2),
            on_next(330, 3), on_next(330, 5), on_next(360, 6),
            on_next(440, 7)]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_mergeconcat_outererror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(
            200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_error(400, ex))

        def create():
            return xs.pipe(ops.merge(max_concurrent=2))
        results = scheduler.start(create)

        assert results.messages == [on_next(260, 1), on_next(280, 4), on_next(
            310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_error(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_mergeconcat_innererror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, scheduler.create_cold_observable(
                on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))),
            on_next(260, scheduler.create_cold_observable(
                on_next(20, 4), on_next(70, 5), on_completed(200))),
            on_next(270, scheduler.create_cold_observable(
                on_next(10, 6), on_next(90, 7), on_next(110, 8), on_error(140, ex))),
            on_next(320, scheduler.create_cold_observable(
                on_next(210, 9), on_next(240, 10), on_completed(300))),
            on_completed(400)
            )

        def create():
            return xs.pipe(ops.merge(max_concurrent=2))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(260, 1), on_next(280, 4), on_next(310, 2),
            on_next(330, 3), on_next(330, 5), on_next(360, 6),
            on_next(440, 7), on_next(460, 8), on_error(490, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]

    def test_merge_112233(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(250, 1), on_next(300, 2), on_next(350, 3), on_completed(360))
        ys = scheduler.create_hot_observable(
            on_next(250, 1), on_next(300, 2), on_next(320, 3), on_completed(340))

        def create():
            return xs.pipe(ops.merge(ys))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(250, 1),
            on_next(250, 1),
            on_next(300, 2),
            on_next(300, 2),
            on_next(320, 3),
            on_next(350, 3),
            on_completed(360)]
        assert xs.subscriptions == [subscribe(200, 360)]
