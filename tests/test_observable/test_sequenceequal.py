import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSequenceEqual(unittest.TestCase):
    def test_sequence_equal_equal(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), close(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(720, True), close(720))
        xs.subscriptions.assert_equal(subscribe(200, 720))
        ys.subscriptions.assert_equal(subscribe(200, 720))

    def test_sequence_equal_equal_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), close(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(720, True), close(720))
        xs.subscriptions.assert_equal(subscribe(200, 720))
        ys.subscriptions.assert_equal(subscribe(200, 720))

    def test_sequence_equal_not_equal_left(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 0), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), close(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_left_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 0), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), close(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_right(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), send(350, 8)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(510, False), close(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))
        ys.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequence_equal_not_equal_right_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), send(350, 8)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(510, False), close(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))
        ys.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequence_equal_not_equal_2(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), send(490, 8), send(520, 9), send(580, 10), send(600, 11)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), send(350, 9), send(400, 9), send(410, 10), send(490, 11), send(550, 12), send(560, 13)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(490, False), close(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))
        ys.subscriptions.assert_equal(subscribe(200, 490))

    def test_sequence_equal_not_equal_2_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), send(490, 8), send(520, 9), send(580, 10), send(600, 11)]
        msgs2 = [send(90, 1), send(270, 3), send(280, 4), send(300, 5), send(330, 6), send(340, 7), send(350, 9), send(400, 9), send(410, 10), send(490, 11), send(550, 12), send(560, 13)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(490, False), close(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))
        ys.subscriptions.assert_equal(subscribe(200, 490))

    def test_sequence_equal_not_equal_3(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), close(330)]
        msgs2 = [send(90, 1), send(270, 3), send(400, 4), close(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(420, False), close(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 420))

    def test_sequence_equal_not_equal_3_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), close(330)]
        msgs2 = [send(90, 1), send(270, 3), send(400, 4), close(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(420, False), close(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 420))

    def test_sequence_equal_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), close(330)]
        msgs2 = [send(90, 1), send(270, 3), send(400, 4), close(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)

        def create():
            def comparer(a, b):
                raise Exception(ex)
            return xs.sequence_equal(ys, comparer)
        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        ys.subscriptions.assert_equal(subscribe(200, 270))

    def test_sequence_equal_comparer_throws_sym(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), close(330)]
        msgs2 = [send(90, 1), send(270, 3), send(400, 4), close(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)

        def create():
            def comparer(a, b):
                raise Exception(ex)
            return ys.sequence_equal(xs, comparer)
        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        ys.subscriptions.assert_equal(subscribe(200, 270))

    def test_sequence_equal_not_equal_4(self):
        scheduler = TestScheduler()
        msgs1 = [send(250, 1), close(300)]
        msgs2 = [send(290, 1), send(310, 2), close(350)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_4_sym(self):
        scheduler = TestScheduler()
        msgs1 = [send(250, 1), close(300)]
        msgs2 = [send(290, 1), send(310, 2), close(350)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_equal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7])

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(510, True), close(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_notequal_elements(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            return xs.sequence_equal([3, 4, 9, 6, 7])

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_comparer_equal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            def comparer(x, y):
                return x % 2 == y % 2
            return xs.sequence_equal([3 - 2, 4, 5, 6 + 42, 7 - 6], comparer)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(510, True), close(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_comparer_notequal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            def comparer(x, y):
                return x % 2 == y % 2
            return xs.sequence_equal([3 - 2, 4, 5 + 9, 6 + 42, 7 - 6], comparer)

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(310, False), close(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_comparer_throws(self):
        def throw_comparer(value, exn):
            def comparer(x, y):
                if x == value:
                    raise Exception(exn)

                return x == y
            return comparer

        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7], throw_comparer(5, ex))

        res = scheduler.start(create=create)

        res.messages.assert_equal(throw(310, ex))
        xs.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_notequal_toolong(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7, 8])

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(510, False), close(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_notequal_tooshort(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), send(310, 5), send(340, 6), send(450, 7), close(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6])

        res = scheduler.start(create=create)

        res.messages.assert_equal(send(450, False), close(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_sequenceequal_enumerable_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 1), send(190, 2), send(240, 3), send(290, 4), throw(310, ex))

        def create():
            return xs.sequence_equal([3, 4])

        res = scheduler.start(create=create)

        res.messages.assert_equal(throw(310, ex))
        xs.subscriptions.assert_equal(subscribe(200, 310))
