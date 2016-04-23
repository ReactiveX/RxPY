import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSwitch(unittest.TestCase):

    def test_switch_data(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(650))

    def test_switch_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_error(50, ex))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(450, ex))

    def test_switch_outer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_error(500, ex))

        def create():
            return xs.switch_latest()
        results = scheduler.start(create)
        results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(500, ex))

    def test_switch_no_inner(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(500))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(500))

    def test_switch_inner_completes(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_completed(540))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(420, 104), on_next(510, 105), on_next(520, 106), on_completed(540))

