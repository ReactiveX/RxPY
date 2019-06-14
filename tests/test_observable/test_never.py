import unittest

from rx import never
from rx.internal.utils import subscribe as _subscribe
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestNever(unittest.TestCase):
    def test_never_basic(self):
        scheduler = TestScheduler()
        xs = never()
        results = scheduler.create_observer()
        _subscribe(xs, results)
        scheduler.start()
        assert results.messages == []
