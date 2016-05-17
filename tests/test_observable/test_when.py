import unittest
from datetime import datetime

from rx.core import Observable
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


    def test_then3_throws(self):
        ex = Exception()
        N = 3

        scheduler = TestScheduler()
        obs = []

        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c):
                raise ex
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_error(210, ex)
        )

    def test_and4(self):
        N = 4
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d):
                return a + b + c + d
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))

    def test_and4_error(self):
        ex = 'ex'
        N = 4

        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d):
                    return a + b + c + d
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).then_do(selector))

            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_then4_throws(self):
        ex = 'ex'
        N = 4
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d):
                raise Exception(ex)
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))

    def test_and5(self):
        N = 5
        scheduler = TestScheduler()
        obs = []
        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e):
                return a + b + c + d + e
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))

    def test_and5_error(self):
        ex = 'ex'
        N = 5
        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d, e):
                    return a + b + c + d + e
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).then_do(selector))

            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_then5_throws(self):
        ex = 'ex'
        N = 5
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e):
                raise Exception(ex)
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))

    def test_and6(self):
        N = 6
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e, f):
                return a + b + c + d + e + f
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))

    def test_and6_error(self):
        ex = 'ex'
        N = 6
        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d, e, f):
                    return a + b + c + d + e + f
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).then_do(selector))

            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_Then6Throws(self):
        ex = 'ex'
        N = 6
        scheduler = TestScheduler()
        obs = []
        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))


        def create():
            def selector(*args):
                raise Exception(ex)
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))

    def test_and7(self):
        N = 7
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e, f, g):
                return a + b + c + d + e + f + g
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))


    def test_and7_error(self):
        ex = 'ex'
        N = 7
        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d, e, f, g):
                    return a + b + c + d + e + f + g
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).then_do(selector))

            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_then7_throws(self):
        ex = 'ex'
        N = 7
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(*args):
                raise Exception(ex)

            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))


    def test_and8(self):
        N = 8
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e, f, g, h):
                return a + b + c + d + e + f + g + h
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))

    def test_and8_error(self):
        ex = 'ex'
        N = 8
        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d, e, f, g, h):
                    return a + b + c + d + e + f + g + h
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).then_do(selector))
            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_then8_throws(self):
        ex = 'ex'
        N = 8
        scheduler = TestScheduler()
        obs = []
        for _ in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(*args):
                raise Exception(ex)

            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))

    def test_And9(self):
        N = 9
        scheduler = TestScheduler()
        obs = []
        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(a, b, c, d, e, f, g, h, _i):
                return a + b + c + d + e + f + g + h + _i
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).and_(obs[8]).then_do(selector))
        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, N), on_completed(220))

    def test_and9_error(self):
        ex = 'ex'
        N = 9
        for i in range(N):
            scheduler = TestScheduler()
            obs = []
            for j in range(N):
                if j == i:
                    obs.append(scheduler.create_hot_observable(on_error(210, ex)))
                else:
                    obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

            def create():
                def selector(a, b, c, d, e, f, g, h, _i):
                    return a + b + c + d + e + f + g + h + _i
                return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).and_(obs[8]).then_do(selector))

            results = scheduler.start(create)
            results.messages.assert_equal(on_error(210, ex))

    def test_then9_throws(self):
        ex = 'ex'
        N = 9
        scheduler = TestScheduler()
        obs = []
        for i in range(N):
            obs.append(scheduler.create_hot_observable(on_next(210, 1), on_completed(220)))

        def create():
            def selector(*args):
                raise Exception(ex)
            return Observable.when(obs[0].and_(obs[1]).and_(obs[2]).and_(obs[3]).and_(obs[4]).and_(obs[5]).and_(obs[6]).and_(obs[7]).and_(obs[8]).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(210, ex))

    def test_WhenMultipleDataSymmetric(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_completed(240)
        )

        ys = scheduler.create_hot_observable(
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270)
        )

        def create():
            def selector(x, y):
                return x + y
            return Observable.when(xs.and_(ys).then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(240, 1 + 4),
            on_next(250, 2 + 5),
            on_next(260, 3 + 6),
            on_completed(270)
        )

    def test_WhenMultipleDataAsymmetric(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_completed(240)
        )

        ys = scheduler.create_hot_observable(
            on_next(240, 4),
            on_next(250, 5),
            on_completed(270)
        )

        def create():
            def selector(x, y):
                return x + y
            return Observable.when(xs.and_(ys).then_do(selector))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(240, 1 + 4),
            on_next(250, 2 + 5),
            on_completed(270)
        )

    def test_when_empty_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(240))
        ys = scheduler.create_hot_observable(on_completed(270))

        def create():
            def selector(x, y):
                return x + y
            return Observable.when(xs.and_(ys).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(270))

    def test_when_never_never(self):
        scheduler = TestScheduler()
        xs = Observable.never()
        ys = Observable.never()

        def create():
            def selector(x, y):
                return x + y
            return Observable.when(xs.and_(ys).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_when_throw_non_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(240, ex))
        ys = scheduler.create_hot_observable(on_completed(270))

        def create():
            def selector(x, y):
                return x + y
            return Observable.when(xs.and_(ys).then_do(selector))

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(240, ex))

    def test_complicated_when(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
        ys = scheduler.create_hot_observable(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
        zs = scheduler.create_hot_observable(on_next(220, 7), on_next(230, 8), on_next(240, 9), on_completed(300))

        def create():
            def sel1(x, y):
                return x + y
            def sel2(x, z):
                return x * z
            def sel3(y, z):
                return y - z
            return Observable.when(xs.and_(ys).then_do(sel1), xs.and_(zs).then_do(sel2), ys.and_(zs).then_do(sel3))

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(220, 1 * 7), on_next(230, 2 * 8), on_next(240, 3 + 4), on_next(250, 5 - 9), on_completed(300))

if __name__ == '__main__':
    unittest.main()
