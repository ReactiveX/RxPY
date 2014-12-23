import unittest
from datetime import datetime

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime
from rx.disposables import SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

class TestWhen(unittest.TestCase):
    def test_then1(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_completed(220)
        )

        def create():
            def selector(a):
                return a
            return Observable.when(xs.then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, 1),
            on_completed(220)
        )

    def test_then1_error(self):
        ex = Exception()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_error(210, ex)
        )

        def create():
            def selector(a):
                return a
            return Observable.when(xs.then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_error(210, ex)
       )

    def test_then1_throws(self):
        ex = Exception()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_completed(220)
        )

        def create():
            def selector(a):
                raise ex
            return Observable.when(xs.then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_error(210, ex)
        )

    def test_and2(self):
        scheduler = TestScheduler()
        N = 2

        obs = []
        for n in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b):
                return a + b
            return Observable.when(obs[0].and_(obs[1]).then_do(selector))
        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, N),
            on_completed(220)
        )

    def test_and2_error(self):
        ex = Exception()
        N = 2

        for n in range(N):
            scheduler = TestScheduler()

            obs = []
            for j in range(N):
                if j == n:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b):
                    return a + b
                return Observable.when(obs[0].and_(obs[1]).then_do(selector))

            results = scheduler.start(create)

            results.messages.assert_equal(
                on_error(210, ex)
            )

    def test_then2_throws(self):
        scheduler = TestScheduler()
        ex = Exception()
        obs = []
        N = 2

        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b):
                raise ex
            return Observable.when(obs[0].and_(obs[1]).then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_error(210, ex)
        )

    def test_and3(self):
        scheduler = TestScheduler()
        obs = []
        N = 3

        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c):
                return a + b + c
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, N),
            on_completed(220)
        )

    def test_and3_error(self):
        ex = Exception()
        N = 3

        for i in range(N):
            scheduler = TestScheduler()

            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c):
                    return a + b + c
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).then_do(selector))
            results = scheduler.start(create)

            results.messages.assert_equal(
                on_error(210, ex)
            )


# def test_Then3Throws(self):
#     ex = Exception()

#     N = 3

#     scheduler = TestScheduler()

#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }

#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).then_do(function (a, b, c) {
#             throw ex
#
#

#     results.messages.assert_equal(
#         on_error(210, ex)
#     )
#

# def test_And4(self):
#     N, i, obs, results, scheduler
#     N = 4
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).then_do(function (a, b, c, d) {
#             return a + b + c + d
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And4Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 4
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).then_do(function (a, b, c, d) {
#                 return a + b + c + d
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then4Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 4
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).then_do(function (a, b, c, d) {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_And5(self):
#     N, i, obs, results, scheduler
#     N = 5
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).then_do(function (a, b, c, d, e) {
#             return a + b + c + d + e
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And5Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 5
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).then_do(function (a, b, c, d, e) {
#                 return a + b + c + d + e
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then5Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 5
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).then_do(function (a, b, c, d, e) {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_And6(self):
#     N, i, obs, results, scheduler
#     N = 6
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).then_do(function (a, b, c, d, e, f) {
#             return a + b + c + d + e + f
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And6Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 6
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).then_do(function (a, b, c, d, e, f) {
#                 return a + b + c + d + e + f
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then6Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 6
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).then_do(function () {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_And7(self):
#     N, i, obs, results, scheduler
#     N = 7
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).then_do(function (a, b, c, d, e, f, g) {
#             return a + b + c + d + e + f + g
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And7Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 7
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).then_do(function (a, b, c, d, e, f, g) {
#                 return a + b + c + d + e + f + g
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then7Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 7
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).then_do(function () {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_And8(self):
#     N, i, obs, results, scheduler
#     N = 8
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).then_do(function (a, b, c, d, e, f, g, h) {
#             return a + b + c + d + e + f + g + h
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And8Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 8
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).then_do(function (a, b, c, d, e, f, g, h) {
#                 return a + b + c + d + e + f + g + h
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then8Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 8
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).then_do(function () {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_And9(self):
#     N, i, obs, results, scheduler
#     N = 9
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).and(obs[8]).then_do(function (a, b, c, d, e, f, g, h, _i) {
#             return a + b + c + d + e + f + g + h + _i
#
#
#     results.messages.assert_equal(on_next(210, N), on_completed(220))
#

# def test_And9Error(self):
#     N, ex, i, j, obs, results, scheduler
#     ex = 'ex'
#     N = 9
#     for (i = 0 i < N i++) {
#         scheduler = TestScheduler()
#         obs = []
#         for (j = 0 j < N j++) {
#             if (j === i) {
#                 obs.append(scheduler.create_hot_observable(on_error(210, ex)))
#             } else {
#                 obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#             }
#         }

#         results = scheduler.start(create)
#             return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).and(obs[8]).then_do(function (a, b, c, d, e, f, g, h, _i) {
#                 return a + b + c + d + e + f + g + h + _i
#
#
#         results.messages.assert_equal(on_error(210, ex))
#     }
#

# def test_Then9Throws(self):
#     N, ex, i, obs, results, scheduler
#     ex = 'ex'
#     N = 9
#     scheduler = TestScheduler()
#     obs = []
#     for (i = 0 i < N i++) {
#         obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))
#     }
#     results = scheduler.start(create)
#         return Observable.when(obs[0].and(obs[1]).and(obs[2]).and(obs[3]).and(obs[4]).and(obs[5]).and(obs[6]).and(obs[7]).and(obs[8]).then_do(function () {
#             throw ex
#
#
#     results.messages.assert_equal(on_error(210, ex))
#

# def test_WhenMultipleDataSymmetric(self):
#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#         on_next(210, 1),
#         on_next(220, 2),
#         on_next(230, 3),
#         on_completed(240)
#     )

#     ys = scheduler.create_hot_observable(
#         on_next(240, 4),
#         on_next(250, 5),
#         on_next(260, 6),
#         on_completed(270)
#     )

#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#
#

#     results.messages.assert_equal(
#         on_next(240, 1 + 4),
#         on_next(250, 2 + 5),
#         on_next(260, 3 + 6),
#         on_completed(270)
#     )
#

# def test_WhenMultipleDataAsymmetric(self):
#     scheduler = TestScheduler()

#     xs = scheduler.create_hot_observable(
#         on_next(210, 1),
#         on_next(220, 2),
#         on_next(230, 3),
#         on_completed(240)
#     )

#     ys = scheduler.create_hot_observable(
#         on_next(240, 4),
#         on_next(250, 5),
#         on_completed(270)
#     )

#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#
#

#     results.messages.assert_equal(
#         on_next(240, 1 + 4),
#         on_next(250, 2 + 5),
#         on_completed(270)
#     )
#

# def test_WhenEmptyEmpty(self):
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_completed(240))
#     ys = scheduler.create_hot_observable(on_completed(270))
#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#
#
#     results.messages.assert_equal(on_completed(270))
#

# def test_WhenNeverNever(self):
#     results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = Observable.never()
#     ys = Observable.never()
#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#
#
#     results.messages.assert_equal()
#

# def test_WhenThrowNonEmpty(self):
#     ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(240, ex))
#     ys = scheduler.create_hot_observable(on_completed(270))
#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#
#
#     results.messages.assert_equal(on_error(240, ex))
#

# def test_ComplicatedWhen(self):
#     results, scheduler, xs, ys, zs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     ys = scheduler.create_hot_observable(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     zs = scheduler.create_hot_observable(on_next(220, 7), on_next(230, 8), on_next(240, 9), on_completed(300))
#     results = scheduler.start(create)
#         return Observable.when(xs.and(ys).then_do(function (x, y) {
#             return x + y
#         }), xs.and(zs).then_do(function (x, z) {
#             return x * z
#         }), ys.and(zs).then_do(function (y, z) {
#             return y - z
#
#
#     results.messages.assert_equal(on_next(220, 1 * 7), on_next(230, 2 * 8), on_next(240, 3 + 4), on_next(250, 5 - 9), on_completed(300))
#

if __name__ == '__main__':
    unittest.main()
