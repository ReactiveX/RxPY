import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable, BooleanDisposable

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

class TestFromArray(unittest.TestCase):
    def test_subscribe_to_enumerable_finite(self):
        enumerable_finite = [1, 2, 3, 4, 5]
        scheduler = TestScheduler()

        def create():
            return Observable.from_(enumerable_finite, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(
                            on_next(201, 1),
                            on_next(202, 2),
                            on_next(203, 3),
                            on_next(204, 4),
                            on_next(205, 5),
                            on_completed(206)
                        )

    def test_subscribe_to_enumerable_empty(self):
      enumerable_finite = []

      scheduler = TestScheduler()

      def create():
          return Observable.from_(enumerable_finite, scheduler=scheduler)
      results = scheduler.start(create)

      results.messages.assert_equal(on_completed(201))