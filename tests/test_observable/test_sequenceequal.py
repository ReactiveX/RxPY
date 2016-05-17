import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSequenceEqual(unittest.TestCase):
    def test_sequence_equal_equal(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(720, True), on_completed(720))
        xs.subscriptions.assert_equal(subscribe(200, 720))
        ys.subscriptions.assert_equal(subscribe(200, 720))

    def test_sequence_equal_equal_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(720, True), on_completed(720))
        xs.subscriptions.assert_equal(subscribe(200, 720))
        ys.subscriptions.assert_equal(subscribe(200, 720))

    def test_sequence_equal_not_equal_left(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 0), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(310, False), on_completed(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_left_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 0), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(310, False), on_completed(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_right(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 8)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(510, False), on_completed(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))
        ys.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequence_equal_not_equal_right_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 8)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(510, False), on_completed(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))
        ys.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequence_equal_not_equal_2(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_next(490, 8), on_next(520, 9), on_next(580, 10), on_next(600, 11)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 9), on_next(400, 9), on_next(410, 10), on_next(490, 11), on_next(550, 12), on_next(560, 13)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(490, False), on_completed(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))
        ys.subscriptions.assert_equal(subscribe(200, 490))

    def test_sequence_equal_not_equal_2_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_next(490, 8), on_next(520, 9), on_next(580, 10), on_next(600, 11)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 9), on_next(400, 9), on_next(410, 10), on_next(490, 11), on_next(550, 12), on_next(560, 13)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(490, False), on_completed(490))
        xs.subscriptions.assert_equal(subscribe(200, 490))
        ys.subscriptions.assert_equal(subscribe(200, 490))

    def test_sequence_equal_not_equal_3(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(420, False), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 420))

    def test_sequence_equal_not_equal_3_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(420, False), on_completed(420))
        xs.subscriptions.assert_equal(subscribe(200, 420))
        ys.subscriptions.assert_equal(subscribe(200, 420))

    def test_sequence_equal_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)

        def create():
            def comparer(a, b):
                raise Exception(ex)
            return xs.sequence_equal(ys, comparer)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        ys.subscriptions.assert_equal(subscribe(200, 270))

    def test_sequence_equal_comparer_throws_sym(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
        msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)

        def create():
            def comparer(a, b):
                raise Exception(ex)
            return ys.sequence_equal(xs, comparer)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        ys.subscriptions.assert_equal(subscribe(200, 270))

    def test_sequence_equal_not_equal_4(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(250, 1), on_completed(300)]
        msgs2 = [on_next(290, 1), on_next(310, 2), on_completed(350)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: xs.sequence_equal(ys))

        results.messages.assert_equal(on_next(310, False), on_completed(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequence_equal_not_equal_4_sym(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(250, 1), on_completed(300)]
        msgs2 = [on_next(290, 1), on_next(310, 2), on_completed(350)]
        xs = scheduler.create_hot_observable(msgs1)
        ys = scheduler.create_hot_observable(msgs2)
        results = scheduler.start(create=lambda: ys.sequence_equal(xs))

        results.messages.assert_equal(on_next(310, False), on_completed(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_equal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7])

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(510, True), on_completed(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_notequal_elements(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            return xs.sequence_equal([3, 4, 9, 6, 7])

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(310, False), on_completed(310))
        xs.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_comparer_equal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            def comparer(x, y):
                return x % 2 == y % 2
            return xs.sequence_equal([3 - 2, 4, 5, 6 + 42, 7 - 6], comparer)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(510, True), on_completed(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_comparer_notequal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            def comparer(x, y):
                return x % 2 == y % 2
            return xs.sequence_equal([3 - 2, 4, 5 + 9, 6 + 42, 7 - 6], comparer)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(310, False), on_completed(310))
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
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7], throw_comparer(5, ex))

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(310, ex))
        xs.subscriptions.assert_equal(subscribe(200, 310))

    def test_sequenceequal_enumerable_notequal_toolong(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6, 7, 8])

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(510, False), on_completed(510))
        xs.subscriptions.assert_equal(subscribe(200, 510))

    def test_sequenceequal_enumerable_notequal_tooshort(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))

        def create():
            return xs.sequence_equal([3, 4, 5, 6])

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(450, False), on_completed(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_sequenceequal_enumerable_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_error(310, ex))

        def create():
            return xs.sequence_equal([3, 4])

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(310, ex))
        xs.subscriptions.assert_equal(subscribe(200, 310))
