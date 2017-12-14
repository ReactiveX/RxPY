import unittest
from datetime import timedelta

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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

    def equals(other):
        return other.interval == self.interval and other.value == self.value

    def get_hash_code(self):
        return self.value.get_hash_code() ^ self.interval.get_hash_code()


class TestJoin(unittest.TestCase):

    def test_join_op_normal_i(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))

        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            return xs.join(ys,
                        lambda x: Observable.timer(x.interval),
                        lambda y: Observable.timer(y.interval),
                        lambda x, y: "%s%s" % (x.value, y.value)
            )

        results = scheduler.start(create=create)
        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            send(732, "7wig"),
            send(732, "8wig"),
            send(830, "9rat"),
            close(900)]

    def test_join_op_normal_ii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 200)),
            send(720, TimeInterval(8, 100)),
            close(721))

        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(990))

        def create():
            return xs.join(ys,
                        lambda x: Observable.timer(x.interval),
                        lambda y: Observable.timer(y.interval),
                        lambda x, y: "%s%s" % (x.value, y.value)
            )

        results = scheduler.start(create=create)
        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            send(732, "7wig"),
            send(732, "8wig"),
            close(910)]

    def test_join_op_normal_iii(self):
         scheduler = TestScheduler()
         xs = scheduler.create_hot_observable(
             send(210, TimeInterval(0, 10)),
             send(219, TimeInterval(1, 5)),
             send(240, TimeInterval(2, 10)),
             send(300, TimeInterval(3, 100)),
             send(310, TimeInterval(4, 80)),
             send(500, TimeInterval(5, 90)),
             send(700, TimeInterval(6, 25)),
             send(710, TimeInterval(7, 300)),
             send(720, TimeInterval(8, 100)),
             send(830, TimeInterval(9, 10)),
             close(900))
         ys = scheduler.create_hot_observable(
             send(215, TimeInterval("hat", 20)),
             send(217, TimeInterval("bat", 1)),
             send(290, TimeInterval("wag", 200)),
             send(300, TimeInterval("pig", 10)),
             send(305, TimeInterval("cup", 50)),
             send(600, TimeInterval("yak", 90)),
             send(702, TimeInterval("tin", 20)),
             send(712, TimeInterval("man", 10)),
             send(722, TimeInterval("rat", 200)),
             send(732, TimeInterval("wig", 5)),
             close(800))

         def create():
             return xs.join(ys,
                            lambda x: Observable.timer(x.interval).filter(lambda _: False),
                            lambda y: Observable.timer(y.interval).filter(lambda _: False),
                            lambda x, y: "%s%s" % (x.value, y.value)
             )
         results = scheduler.start(create=create)
         assert results.messages == [
             send(215, "0hat"),
             send(217, "0bat"),
             send(219, "1hat"),
             send(300, "3wag"),
             send(300, "3pig"),
             send(305, "3cup"),
             send(310, "4wag"),
             send(310, "4pig"),
             send(310, "4cup"),
             send(702, "6tin"),
             send(710, "7tin"),
             send(712, "6man"),
             send(712, "7man"),
             send(720, "8tin"),
             send(720, "8man"),
             send(722, "6rat"),
             send(722, "7rat"),
             send(722, "8rat"),
             send(732, "7wig"),
             send(732, "8wig"),
             send(830, "9rat"),
             close(900)]

    def test_join_op_normal_iv(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 200)),
            send(720, TimeInterval(8, 100)),
            close(990))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(980))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            send(732, "7wig"),
            send(732, "8wig"),
            close(980)]

    def test_join_op_normal_v(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 200)),
            send(720, TimeInterval(8, 100)),
            close(990))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(900))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            send(732, "7wig"),
            send(732, "8wig"),
            close(922)]

    def test_join_op_normal_vi(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, TimeInterval(0, 10)),
        send(219, TimeInterval(1, 5)),
        send(240, TimeInterval(2, 10)),
        send(300, TimeInterval(3, 100)),
        send(310, TimeInterval(4, 80)),
        send(500, TimeInterval(5, 90)),
        send(700, TimeInterval(6, 25)),
        send(710, TimeInterval(7, 30)),
        send(720, TimeInterval(8, 200)),
        send(830, TimeInterval(9, 10)),
        close(850))
        ys = scheduler.create_hot_observable(send(215, TimeInterval("hat", 20)),
        send(217, TimeInterval("bat", 1)),
        send(290, TimeInterval("wag", 200)),
        send(300, TimeInterval("pig", 10)),
        send(305, TimeInterval("cup", 50)),
        send(600, TimeInterval("yak", 90)),
        send(702, TimeInterval("tin", 20)),
        send(712, TimeInterval("man", 10)),
        send(722, TimeInterval("rat", 20)),
        send(732, TimeInterval("wig", 5)),
        close(900))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            send(732, "7wig"),
            send(732, "8wig"),
            close(900)]

    def test_join_op_normal_vii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create, disposed=713)
        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man")]

    def test_join_op_error_i(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            throw(310, ex))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create, disposed=713)
        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            throw(310, ex)]

    def test_join_op_error_ii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            throw(722, ex))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            throw(722, ex)]

    def test_join_op_error_iii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval).flat_map(
                    Observable.throw_exception(ex) if x.value == 6 else Observable.empty()),
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            send(722, "6rat"),
            send(722, "7rat"),
            send(722, "8rat"),
            throw(725, ex)]

    def test_join_op_error_iv(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 19)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval).flat_map(
                    Observable.throw_exception(ex) if y.value == "tin" else Observable.empty()),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [
            send(215, "0hat"),
            send(217, "0bat"),
            send(219, "1hat"),
            send(300, "3wag"),
            send(300, "3pig"),
            send(305, "3cup"),
            send(310, "4wag"),
            send(310, "4pig"),
            send(310, "4cup"),
            send(702, "6tin"),
            send(710, "7tin"),
            send(712, "6man"),
            send(712, "7man"),
            send(720, "8tin"),
            send(720, "8man"),
            throw(721, ex)]

    def test_join_op_error_v(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            def left_duration_selector(x):
                if x.value >= 0:
                    raise Exception(ex)
                else:
                    return Observable.empty()

            return xs.join(ys,
                left_duration_selector,
                lambda y: Observable.timer(y.interval),
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [throw(210, ex)]

    def test_join_op_error_vi(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            def right_duration_selector(y):
                if len(y.value) >= 0:
                    raise Exception(ex)
                else:
                    return Observable.empty()

            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                right_duration_selector,
                lambda x, y: str(x.value) + y.value
            )
        results = scheduler.start(create=create)

        assert results.messages == [throw(215, ex)]

    def test_join_op_error_vii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            def result_selector(x, y):
                if x.value >= 0:
                    raise Exception(ex)
                else:
                    return str(x.value) + y.value

            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                result_selector,
                )
        results = scheduler.start(create=create)
        assert results.messages == [throw(215, ex)]

    def test_join_op_error_viii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(210, TimeInterval(0, 10)),
            send(219, TimeInterval(1, 5)),
            send(240, TimeInterval(2, 10)),
            send(300, TimeInterval(3, 100)),
            send(310, TimeInterval(4, 80)),
            send(500, TimeInterval(5, 90)),
            send(700, TimeInterval(6, 25)),
            send(710, TimeInterval(7, 300)),
            send(720, TimeInterval(8, 100)),
            send(830, TimeInterval(9, 10)),
            close(900))
        ys = scheduler.create_hot_observable(
            send(215, TimeInterval("hat", 20)),
            send(217, TimeInterval("bat", 1)),
            send(290, TimeInterval("wag", 200)),
            send(300, TimeInterval("pig", 10)),
            send(305, TimeInterval("cup", 50)),
            send(600, TimeInterval("yak", 90)),
            send(702, TimeInterval("tin", 20)),
            send(712, TimeInterval("man", 10)),
            send(722, TimeInterval("rat", 200)),
            send(732, TimeInterval("wig", 5)),
            close(800))

        def create():
            def result_selector(x, y):
                if x.value >= 0:
                    raise Exception(ex)
                else:
                    return str(x.value) + y.value

            return xs.join(ys,
                lambda x: Observable.timer(x.interval),
                lambda y: Observable.timer(y.interval),
                result_selector,
                )
        results = scheduler.start(create=create)

        assert results.messages == [throw(215, ex)]
