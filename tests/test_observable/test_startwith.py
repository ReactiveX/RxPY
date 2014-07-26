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

class TestStartWith(unittest.TestCase):
    def test_start_with(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))
        
        def create():
            return xs.start_with(1)
        results = scheduler.start(create).messages
        assert(3 ==  len(results))
        assert(results[0].value.kind == 'N' and results[0].value.value == 1 and results[0].time == 200)
        assert(results[1].value.kind == 'N' and results[1].value.value == 2 and results[1].time == 220)
        assert(results[2].value.kind == 'C')
