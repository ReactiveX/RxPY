import unittest
from datetime import timedelta

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

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

    def equals(other):
        return other.interval == self.interval and other.value == self.value

    def get_hash_code(self):
        return self.value.get_hash_code() ^ self.interval.get_hash_code()

def new_timer(l, t, scheduler):
    timer = scheduler.create_cold_observable(on_next(t, 0), on_completed(t))
    l.append(timer)
    return timer

class TestGroup_join(unittest.TestCase):

    def test_group_join_op_normal_i(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, TimeInterval(0, 10)),
            on_next(219, TimeInterval(1, 5)),
            on_next(240, TimeInterval(2, 10)),
            on_next(300, TimeInterval(3, 100)),
            on_next(310, TimeInterval(4, 80)),
            on_next(500, TimeInterval(5, 90)),
            on_next(700, TimeInterval(6, 25)),
            on_next(710, TimeInterval(7, 280)),
            on_next(720, TimeInterval(8, 100)),
            on_next(830, TimeInterval(9, 10)),
            on_completed(900)
        )

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
            on_completed(800)
        )

        xsd = []
        ysd = []

        def create():
            return xs.group_join(
                ys,
                lambda x: new_timer(xsd, x.interval, scheduler),
                lambda y: new_timer(ysd, y.interval, scheduler),
                lambda x, yy: yy.select(lambda y: str(x.value) + y.value)
            ).merge_observable()

        res = scheduler.start(create=create)

        res.messages.assert_equal(
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
            on_completed(990)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 990)
        )

        ys.subscriptions.assert_equal(
            subscribe(200, 990)
        )

# def test_Group_joinOp_Normal_II():
#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#         on_next(210, TimeInterval(0, 10)),
#         on_next(219, TimeInterval(1, 5)),
#         on_next(240, TimeInterval(2, 10)),
#         on_next(300, TimeInterval(3, 100)),
#         on_next(310, TimeInterval(4, 80)),
#         on_next(500, TimeInterval(5, 90)),
#         on_next(700, TimeInterval(6, 25)),
#         on_next(710, TimeInterval(7, 200)),
#         on_next(720, TimeInterval(8, 100)),
#         on_completed(721)
#     )

#     ys = scheduler.create_hot_observable(
#         on_next(215, TimeInterval("hat", (20))),
#         on_next(217, TimeInterval("bat", (1))),
#         on_next(290, TimeInterval("wag", (200))),
#         on_next(300, TimeInterval("pig", (10))),
#         on_next(305, TimeInterval("cup", (50))),
#         on_next(600, TimeInterval("yak", (90))),
#         on_next(702, TimeInterval("tin", (20))),
#         on_next(712, TimeInterval("man", (10))),
#         on_next(722, TimeInterval("rat", (200))),
#         on_next(732, TimeInterval("wig", (5))),
#         on_completed(990)
#     )

#     xsd = []
#     ysd = []

#     res = scheduler.start(create=create)
#         return xs.group_join(
#             ys,
#             function (x) { return newTimer(xsd, x.interval, scheduler) },
#             function (y) { return newTimer(ysd, y.interval, scheduler) },
#             function (x, yy) { return yy.select(function (y) { return x.value + y.value })})
#         .merge_observable()
#     })

#     res.messages.assert_equal(
#         on_next(215, "0hat"),
#         on_next(217, "0bat"),
#         on_next(219, "1hat"),
#         on_next(300, "3wag"),
#         on_next(300, "3pig"),
#         on_next(305, "3cup"),
#         on_next(310, "4wag"),
#         on_next(310, "4pig"),
#         on_next(310, "4cup"),
#         on_next(702, "6tin"),
#         on_next(710, "7tin"),
#         on_next(712, "7man"),
#         on_next(712, "6man"),
#         on_next(720, "8tin"),
#         on_next(720, "8man"),
#         on_next(722, "7rat"),
#         on_next(722, "6rat"),
#         on_next(722, "8rat"),
#         on_next(732, "7wig"),
#         on_next(732, "8wig"),
#         on_completed(910)
#     )

#     xs.subscriptions.assert_equal(
#         subscribe(200, 910)
#     )

#     ys.subscriptions.assert_equal(
#         subscribe(200, 910)
#     )
# })

# def test_Group_joinOp_Normal_III():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, 10)), on_next(219, TimeInterval(1, 5)), on_next(240, TimeInterval(2, 10)), on_next(300, TimeInterval(3, 100)), on_next(310, TimeInterval(4, 80)), on_next(500, TimeInterval(5, 90)), on_next(700, TimeInterval(6, 25)), on_next(710, TimeInterval(7, 280)), on_next(720, TimeInterval(8, 100)), on_next(830, TimeInterval(9, 10)), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", 20)), on_next(217, TimeInterval("bat", 1)), on_next(290, TimeInterval("wag", 200)), on_next(300, TimeInterval("pig", 10)), on_next(305, TimeInterval("cup", 50)), on_next(600, TimeInterval("yak", 90)), on_next(702, TimeInterval("tin", 20)), on_next(712, TimeInterval("man", 10)), on_next(722, TimeInterval("rat", 200)), on_next(732, TimeInterval("wig", 5)), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler).where(function () {
#                 return false
#             })
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler).where(function () {
#                 return false
#             })
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_next(722, "7rat"), on_next(722, "6rat"), on_next(722, "8rat"), on_next(732, "7wig"), on_next(732, "8wig"), on_next(830, "9rat"), on_completed(990))
# })

# def test_Group_joinOp_Normal_IV():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(200))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_completed(990))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(980))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_next(722, "7rat"), on_next(722, "6rat"), on_next(722, "8rat"), on_next(732, "7wig"), on_next(732, "8wig"), on_completed(990))
# })

# def test_Group_joinOp_Normal_V():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(200))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_completed(990))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(900))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_next(722, "7rat"), on_next(722, "6rat"), on_next(722, "8rat"), on_next(732, "7wig"), on_next(732, "8wig"), on_completed(990))
# })

# def test_Group_joinOp_Normal_VI():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(30))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(200))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(850))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(20))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(900))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_next(722, "7rat"), on_next(722, "6rat"), on_next(722, "8rat"), on_next(732, "7wig"), on_next(732, "8wig"), on_completed(920))
# })

# def test_Group_joinOp_Normal_VII():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_completed(210))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(20))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(900))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_completed(210))
# })

# def test_Group_joinOp_Normal_VIII():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(200))))
#     ys = scheduler.create_hot_observable(on_next(220, TimeInterval("hat", TimeSpan.fromTicks(100))), on_completed(230))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(220, "0hat"))
# })

# def test_Group_joinOp_Normal_IX():
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithDispose(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     }, 713)
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"))
# })

# def test_Group_joinOp_Error_I():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_error(310, ex))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_error(310, ex))
# })

# def test_Group_joinOp_Error_II():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_error(722, ex))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_error(722, ex))
# })

# def test_Group_joinOp_Error_III():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler).selectMany(x.value === 6 ? Observable.throwException(ex) : Observable.empty())
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_next(722, "7rat"), on_next(722, "6rat"), on_next(722, "8rat"), on_error(725, ex))
# })

# def test_Group_joinOp_Error_IV():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(19))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler).selectMany(y.value === "tin" ? Observable.throwException(ex) : Observable.empty())
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_next(215, "0hat"), on_next(217, "0bat"), on_next(219, "1hat"), on_next(300, "3wag"), on_next(300, "3pig"), on_next(305, "3cup"), on_next(310, "4wag"), on_next(310, "4pig"), on_next(310, "4cup"), on_next(702, "6tin"), on_next(710, "7tin"), on_next(712, "7man"), on_next(712, "6man"), on_next(720, "8tin"), on_next(720, "8man"), on_error(721, ex))
# })

# def test_Group_joinOp_Error_V():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             if (x.value >= 0) {
#                 throw ex
#             } else {
#                 return Observable.empty()
#             }
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_error(210, ex))
# })

# def test_Group_joinOp_Error_VI():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             if (y.value.length >= 0) {
#                 throw ex
#             } else {
#                 return Observable.empty()
#             }
#         }, function (x, yy) {
#             return yy.select(function (y) {
#                 return x.value + y.value
#             })
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_error(215, ex))
# })

# def test_Group_joinOp_Error_VII():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(215, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(210, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             if (x.value >= 0) {
#                 throw ex
#             } else {
#                 return yy.select(function (y) {
#                     return x.value + y.value
#                 })
#             }
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_error(215, ex))
# })

# def test_Group_joinOp_Error_VIII():
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, TimeInterval(0, TimeSpan.fromTicks(10))), on_next(219, TimeInterval(1, TimeSpan.fromTicks(5))), on_next(240, TimeInterval(2, TimeSpan.fromTicks(10))), on_next(300, TimeInterval(3, TimeSpan.fromTicks(100))), on_next(310, TimeInterval(4, TimeSpan.fromTicks(80))), on_next(500, TimeInterval(5, TimeSpan.fromTicks(90))), on_next(700, TimeInterval(6, TimeSpan.fromTicks(25))), on_next(710, TimeInterval(7, TimeSpan.fromTicks(300))), on_next(720, TimeInterval(8, TimeSpan.fromTicks(100))), on_next(830, TimeInterval(9, TimeSpan.fromTicks(10))), on_completed(900))
#     ys = scheduler.create_hot_observable(on_next(215, TimeInterval("hat", TimeSpan.fromTicks(20))), on_next(217, TimeInterval("bat", TimeSpan.fromTicks(1))), on_next(290, TimeInterval("wag", TimeSpan.fromTicks(200))), on_next(300, TimeInterval("pig", TimeSpan.fromTicks(10))), on_next(305, TimeInterval("cup", TimeSpan.fromTicks(50))), on_next(600, TimeInterval("yak", TimeSpan.fromTicks(90))), on_next(702, TimeInterval("tin", TimeSpan.fromTicks(20))), on_next(712, TimeInterval("man", TimeSpan.fromTicks(10))), on_next(722, TimeInterval("rat", TimeSpan.fromTicks(200))), on_next(732, TimeInterval("wig", TimeSpan.fromTicks(5))), on_completed(800))
#     results = scheduler.startWithCreate(function () {
#         return xs.group_join(ys, function (x) {
#             return Observable.timer(x.interval, undefined, scheduler)
#         }, function (y) {
#             return Observable.timer(y.interval, undefined, scheduler)
#         }, function (x, yy) {
#             if (x.value >= 0) {
#                 throw ex
#             } else {
#                 return yy.select(function (y) {
#                     return x.value + y.value
#                 })
#             }
#         }).merge_observable()
#     })
#     results.messages.assert_equal(on_error(210, ex))
# })


# function arrayEqual (arr1, arr2) {
#     if (arr1.length !== arr2.length) { return false }
#     for (i = 0, len = arr1.length i < len i++) {
#         if (arr1[i] !== arr2[i]) { return false }
#     }
#     return true
# }

# def test_Buffer_Boundaries_Simple():
#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#         on_next(90, 1),
#         on_next(180, 2),
#         on_next(250, 3),
#         on_next(260, 4),
#         on_next(310, 5),
#         on_next(340, 6),
#         on_next(410, 7),
#         on_next(420, 8),
#         on_next(470, 9),
#         on_next(550, 10),
#         on_completed(590)
#     )

#     ys = scheduler.create_hot_observable(
#         on_next(255, true),
#         on_next(330, true),
#         on_next(350, true),
#         on_next(400, true),
#         on_next(500, true),
#         on_completed(900)
#     )

#     res = scheduler.startWithCreate(function () {
#         return xs.buffer(ys)
#     })

#     res.messages.assert_equal(
#         on_next(255, function (b) { return arrayEqual(b, [3]) }),
#         on_next(330, function (b) { return arrayEqual(b, [4, 5]) }),
#         on_next(350, function (b) { return arrayEqual(b, [6]) }),
#         on_next(400, function (b) { return arrayEqual(b, [ ]) }),
#         on_next(500, function (b) { return arrayEqual(b, [7, 8, 9]) }),
#         on_next(590, function (b) { return arrayEqual(b, [10]) }),
#         on_completed(590)
#     )

#     xs.subscriptions.assert_equal(
#         subscribe(200, 590)
#     )

#     ys.subscriptions.assert_equal(
#         subscribe(200, 590)
#     )
# })

# def test_Buffer_Boundaries_on_completedBoundaries():
#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#         on_next(90, 1),
#         on_next(180, 2),
#         on_next(250, 3),
#         on_next(260, 4),
#         on_next(310, 5),
#         on_next(340, 6),
#         on_next(410, 7),
#         on_next(420, 8),
#         on_next(470, 9),
#         on_next(550, 10),
#         on_completed(590)
#     )

#     ys = scheduler.create_hot_observable(
#         on_next(255, true),
#         on_next(330, true),
#         on_next(350, true),
#         on_completed(400)
#     )

#     res = scheduler.startWithCreate(function () {
#         return xs.buffer(ys)
#     })

#     res.messages.assert_equal(
#         on_next(255, function (b) { return arrayEqual(b, [3]) }),
#         on_next(330, function (b) { return arrayEqual(b, [4, 5]) }),
#         on_next(350, function (b) { return arrayEqual(b, [6]) }),
#         on_next(400, function (b) { return arrayEqual(b, []) }),
#         on_completed(400)
#     )

#     xs.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )

#     ys.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )
# })

# def test_Buffer_Boundaries_on_errorSource():
#     ex = 'ex'

#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#             on_next(90, 1),
#             on_next(180, 2),
#             on_next(250, 3),
#             on_next(260, 4),
#             on_next(310, 5),
#             on_next(340, 6),
#             on_next(380, 7),
#             on_error(400, ex)
#     )

#     ys = scheduler.create_hot_observable(
#             on_next(255, true),
#             on_next(330, true),
#             on_next(350, true),
#             on_completed(500)
#     )

#     res = scheduler.startWithCreate(function () {
#         return xs.buffer(ys)
#     })

#     res.messages.assert_equal(
#         on_next(255, function (b) { return arrayEqual(b, [3]) }),
#         on_next(330, function (b) { return arrayEqual(b, [4, 5]) }),
#         on_next(350, function (b) { return arrayEqual(b, [6]) }),
#         on_error(400, ex)
#     )

#     xs.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )

#     ys.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )
# })

# def test_Buffer_Boundaries_on_errorBoundaries():
#     ex = 'ex'

#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#             on_next(90, 1),
#             on_next(180, 2),
#             on_next(250, 3),
#             on_next(260, 4),
#             on_next(310, 5),
#             on_next(340, 6),
#             on_next(410, 7),
#             on_next(420, 8),
#             on_next(470, 9),
#             on_next(550, 10),
#             on_completed(590)
#     )

#     ys = scheduler.create_hot_observable(
#             on_next(255, true),
#             on_next(330, true),
#             on_next(350, true),
#             on_error(400, ex)
#     )

#     res = scheduler.startWithCreate(function () {
#         return xs.buffer(ys)
#     })

#     res.messages.assert_equal(
#         on_next(255, function (b) { return arrayEqual(b, [3]) }),
#         on_next(330, function (b) { return arrayEqual(b, [4, 5]) }),
#         on_next(350, function (b) { return arrayEqual(b, [6]) }),
#         on_error(400, ex)
#     )

#     xs.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )

#     ys.subscriptions.assert_equal(
#         subscribe(200, 400)
#     )
# })

# // must call `QUnit.start()` if using QUnit < 1.3.0 with Node.js or any
# // version of QUnit with Narwhal, Rhino, or RingoJS

# }(typeof global == 'object' && global || this))

if __name__ == '__main__':
    unittest.main()