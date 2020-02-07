import unittest
from datetime import timedelta

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TimeSpan(object):
    def from_ticks(self, value):
        return value


class TimeInterval(object):
    def __init__(self, value, interval):
        if isinstance(interval, timedelta):
            interval = int(interval.microseconds/1000)

        self.value = value
        self.interval = interval

    def __str__(self):
        return "%s@%s" % (self.value, self.interval)

    def equals(self, other):
        return other.interval == self.interval and other.value == self.value

    def get_hash_code(self):
        return self.value.get_hash_code() ^ self.interval.get_hash_code()


class TestJoin(unittest.TestCase):

    def test_join_op_normal_i(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))

        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)
        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_next(732, "7wig"),
            on_next(732, "8wig"),
            on_next(830, "9rat"),
            on_completed(900)]

    def test_join_op_normal_ii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 200)),
            on_next(720, TimeInterval(8, 100)),
            on_completed(721))

        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(990))


        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)
        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_next(732, "7wig"),
            on_next(732, "8wig"),
            on_completed(910)]

    def test_join_op_normal_iii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
             on_next(210, TimeInterval(0, 10)),
             on_next(219, TimeInterval(1, 5)),
             on_next(240, TimeInterval(2, 10)),
             on_next(300, TimeInterval(3, 100)),
             on_next(310, TimeInterval(4, 80)),
             on_next(500, TimeInterval(5, 90)),
             on_next(700, TimeInterval(6, 25)),
             on_next(710, TimeInterval(7, 300)),
             on_next(720, TimeInterval(8, 100)),
             on_next(830, TimeInterval(9, 10)),
             on_completed(900))
        ys = scheduler.create_hot_observable(
             on_next(215, TimeInterval("hat", 20)),
             on_next(217, TimeInterval("bat", 1)),
             on_next(290, TimeInterval("wag", 200)),
             on_next(300, TimeInterval("pig", 10)),
             on_next(305, TimeInterval("cup", 50)),
             on_next(600, TimeInterval("yak", 90)),
             on_next(702, TimeInterval("tin", 20)),
             on_next(712, TimeInterval("man", 10)),
             on_next(722, TimeInterval("rat", 200)),
             on_next(732, TimeInterval("wig", 5)),
             on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval).pipe(ops.filter(lambda _: False)),
                    lambda y: rx.timer(y.interval).pipe(ops.filter(lambda _: False)),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)
        assert results.messages == [
             on_next(215, "0hat"),
             on_next(217, "0bat"),
             on_next(219, "1hat"),
             on_next(300, "3wag"),
             on_next(300, "3pig"),
             on_next(305, "3cup"),
             on_next(310, "4wag"),
             on_next(310, "4pig"),
             on_next(310, "4cup"),
             on_next(702, "6tin"),
             on_next(710, "7tin"),
             on_next(712, "6man"),
             on_next(712, "7man"),
             on_next(720, "8tin"),
             on_next(720, "8man"),
             on_next(722, "6rat"),
             on_next(722, "7rat"),
             on_next(722, "8rat"),
             on_next(732, "7wig"),
             on_next(732, "8wig"),
             on_next(830, "9rat"),
             on_completed(900)]

    def test_join_op_normal_iv(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 200)),
            on_next(720, TimeInterval(8, 100)),
            on_completed(990))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(980))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_next(732, "7wig"),
            on_next(732, "8wig"),
            on_completed(980)]

    def test_join_op_normal_v(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 200)),
            on_next(720, TimeInterval(8, 100)),
            on_completed(990))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(900))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_next(732, "7wig"),
            on_next(732, "8wig"),
            on_completed(922)]

    def test_join_op_normal_vi(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 30)),
            on_next(720, TimeInterval(8, 200)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(850))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 20)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(900))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_next(732, "7wig"),
            on_next(732, "8wig"),
            on_completed(900)]

    def test_join_op_normal_vii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create, disposed=713)
        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man")]

    def test_join_op_error_i(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_error(310, ex))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                    )

        results = scheduler.start(create=create, disposed=713)
        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_error(310, ex)]

    def test_join_op_error_ii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_error(722, ex))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_error(722, ex)]

    def test_join_op_error_iii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval).pipe(ops.flat_map(rx.throw(ex) if x.value == 6 else rx.empty())),
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_next(722, "6rat"),
            on_next(722, "7rat"),
            on_next(722, "8rat"),
            on_error(725, ex)]

    def test_join_op_error_iv(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 19)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    lambda y: rx.timer(y.interval).pipe(ops.flat_map(rx.throw(ex) if y.value == "tin" else rx.empty())),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(215, "0hat"),
            on_next(217, "0bat"),
            on_next(219, "1hat"),
            on_next(300, "3wag"),
            on_next(300, "3pig"),
            on_next(305, "3cup"),
            on_next(310, "4wag"),
            on_next(310, "4pig"),
            on_next(310, "4cup"),
            on_next(702, "6tin"),
            on_next(710, "7tin"),
            on_next(712, "6man"),
            on_next(712, "7man"),
            on_next(720, "8tin"),
            on_next(720, "8man"),
            on_error(721, ex)]

    def test_join_op_error_v(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def left_duration_mapper(x):
                if x.value >= 0:
                    raise Exception(ex)
                else:
                    return rx.empty()

            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    left_duration_mapper,
                    lambda y: rx.timer(y.interval),
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [on_error(210, ex)]

    def test_join_op_error_vi(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 300)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900))
        ys = scheduler.create_hot_observable(
            on_next(215, TimeInterval("hat", 20)),
            on_next(217, TimeInterval("bat", 1)),
            on_next(290, TimeInterval("wag", 200)),
            on_next(300, TimeInterval("pig", 10)),
            on_next(305, TimeInterval("cup", 50)),
            on_next(600, TimeInterval("yak", 90)),
            on_next(702, TimeInterval("tin", 20)),
            on_next(712, TimeInterval("man", 10)),
            on_next(722, TimeInterval("rat", 200)),
            on_next(732, TimeInterval("wig", 5)),
            on_completed(800))

        def create():
            def right_duration_mapper(y):
                if len(y.value) >= 0:
                    raise Exception(ex)
                else:
                    return rx.empty()

            def mapper(xy):
                x, y = xy
                return "{}{}".format(x.value, y.value)

            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: rx.timer(x.interval),
                    right_duration_mapper,
                    ),
                ops.map(mapper),
                )

        results = scheduler.start(create=create)

        assert results.messages == [on_error(215, ex)]

    def test_join_op_forward_scheduler(self):
        scheduler = TestScheduler()

        subscribe_schedulers = {
            'x': 'unknown',
            'y': 'unknown',
            'duration_x': 'unknown',
            'duration_y': 'unknown',
            }

        def subscribe_x(observer, scheduler='not_set'):
            subscribe_schedulers['x'] = scheduler
            # need to push one element to trigger duration mapper
            observer.on_next('foo')

        def subscribe_y(observer, scheduler='not_set'):
            subscribe_schedulers['y'] = scheduler
            # need to push one element to trigger duration mapper
            observer.on_next('bar')

        def subscribe_duration_x(observer, scheduler='not_set'):
            subscribe_schedulers['duration_x'] = scheduler

        def subscribe_duration_y(observer, scheduler='not_set'):
            subscribe_schedulers['duration_y'] = scheduler

        xs = rx.create(subscribe_x)
        ys = rx.create(subscribe_y)
        duration_x = rx.create(subscribe_duration_x)
        duration_y = rx.create(subscribe_duration_y)

        def create():
            return xs.pipe(
                ops.join(
                    ys,
                    lambda x: duration_x,
                    lambda y: duration_y,
                    ),
                )

        results = scheduler.start(create=create)
        assert subscribe_schedulers['x'] is scheduler
        assert subscribe_schedulers['y'] is scheduler
        assert subscribe_schedulers['duration_x'] is scheduler
        assert subscribe_schedulers['duration_y'] is scheduler

    def test_join_op_forward_scheduler_None(self):

        subscribe_schedulers = {
            'x': 'unknown',
            'y': 'unknown',
            'duration_x': 'unknown',
            'duration_y': 'unknown',
            }

        def subscribe_x(observer, scheduler='not_set'):
            subscribe_schedulers['x'] = scheduler
            # need to push one element to trigger duration mapper
            observer.on_next('foo')

        def subscribe_y(observer, scheduler='not_set'):
            subscribe_schedulers['y'] = scheduler
            # need to push one element to trigger duration mapper
            observer.on_next('bar')

        def subscribe_duration_x(observer, scheduler='not_set'):
            subscribe_schedulers['duration_x'] = scheduler

        def subscribe_duration_y(observer, scheduler='not_set'):
            subscribe_schedulers['duration_y'] = scheduler

        xs = rx.create(subscribe_x)
        ys = rx.create(subscribe_y)
        duration_x = rx.create(subscribe_duration_x)
        duration_y = rx.create(subscribe_duration_y)

        stream = xs.pipe(
            ops.join(
                ys,
                lambda x: duration_x,
                lambda y: duration_y,
                ),
            )

        stream.subscribe()
        assert subscribe_schedulers['x'] is None
        assert subscribe_schedulers['y'] is None
        assert subscribe_schedulers['duration_x'] is None
        assert subscribe_schedulers['duration_y'] is None

