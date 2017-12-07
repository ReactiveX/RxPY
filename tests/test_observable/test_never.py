import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestNever(unittest.TestCase):
    def test_never_basic(self):
        scheduler = TestScheduler()
        xs = Observable.never()
        results = scheduler.create_observer()
        xs.subscribe(results)
        scheduler.start()
        results.messages.assert_equal()
