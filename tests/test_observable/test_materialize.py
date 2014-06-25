import unittest

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

class Test_materialize(unittest.TestCase):

    def test_materialize_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().materialize()

        results = scheduler.start(create)
        results.messages.assert_equal()

    # def test_Materialize_Empty():
    #     var results, scheduler, xs
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
    #     results = scheduler.start(create)
    #         return xs.materialize()
    #     }).messages
    #     equal(2, results.length)
    #     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'C' and results[0].time == 250)
    #     assert(results[1].value.kind == 'C' and results[1].time == 250)

    # def test_Materialize_Return():
    #     var results, scheduler, xs
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
    #     results = scheduler.start(create)
    #         return xs.materialize()
    #     }).messages
    #     equal(3, results.length)
    #     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'N' and results[0].value.value.value == 2 and results[0].time == 210)
    #     assert(results[1].value.kind == 'N' and results[1].value.value.kind == 'C' and results[1].time == 250)
    #     assert(results[2].value.kind == 'C' and results[1].time == 250)

    # def test_Materialize_Throw():
    #     var ex, results, scheduler, xs
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
    #     results = scheduler.start(create)
    #         return xs.materialize()
    #     }).messages
    #     equal(2, results.length)
    #     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'E' and results[0].value.value.exception == ex)
    #     assert(results[1].value.kind == 'C')

    # def test_Materialize_Dematerialize_Never():
    #     var results, scheduler
    #     scheduler = TestScheduler()
    #     results = scheduler.start(create)
    #         return Rx.Observable.never().materialize().dematerialize()
    
    #     results.messages.assert_equal()

    # def test_Materialize_Dematerialize_Empty():
    #     var results, scheduler, xs
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
    #     results = scheduler.start(create)
    #         return xs.materialize().dematerialize()
    #     }).messages
    #     equal(1, results.length)
    #     assert(results[0].value.kind == 'C' and results[0].time == 250)

    # def test_Materialize_Dematerialize_Return():
    #     var results, scheduler, xs
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
    #     results = scheduler.start(create)
    #         return xs.materialize().dematerialize()
    #     }).messages
    #     equal(2, results.length)
    #     assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 210)
    #     assert(results[1].value.kind == 'C')

    # def test_Materialize_Dematerialize_Throw():
    #     var ex, results, scheduler, xs
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
    #     results = scheduler.start(create)
    #         return xs.materialize().dematerialize()
    #     }).messages
    #     equal(1, results.length)
    #     assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

if __name__ == '__main__':
    unittest.main()
