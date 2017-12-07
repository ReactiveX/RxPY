import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSwitch(unittest.TestCase):

    def test_switch_data(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), send(110, 103), send(120, 104), send(210, 105), send(220, 106), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), close(50))), send(500, scheduler.create_cold_observable(send(10, 301), send(20, 302), send(30, 303), send(40, 304), close(150))), close(600))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), send(510, 301), send(520, 302), send(530, 303), send(540, 304), close(650))

    def test_switch_inner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), send(110, 103), send(120, 104), send(210, 105), send(220, 106), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), throw(50, ex))), send(500, scheduler.create_cold_observable(send(10, 301), send(20, 302), send(30, 303), send(40, 304), close(150))), close(600))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), throw(450, ex))

    def test_switch_outer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), send(110, 103), send(120, 104), send(210, 105), send(220, 106), close(230))), send(400, scheduler.create_cold_observable(send(10, 201), send(20, 202), send(30, 203), send(40, 204), close(50))), throw(500, ex))

        def create():
            return xs.switch_latest()
        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 201), send(420, 202), send(430, 203), send(440, 204), throw(500, ex))

    def test_switch_no_inner(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(500))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(close(500))

    def test_switch_inner_completes(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(300, scheduler.create_cold_observable(send(10, 101), send(20, 102), send(110, 103), send(120, 104), send(210, 105), send(220, 106), close(230))), close(540))

        def create():
            return xs.switch_latest()

        results = scheduler.start(create)
        results.messages.assert_equal(send(310, 101), send(320, 102), send(410, 103), send(420, 104), send(510, 105), send(520, 106), close(540))

