"""
Tests which work with backports of asyncio to Py2, i.e. w/o the language
additions
"""

import unittest

from nose import SkipTest
import rx
asyncio = rx.config['asyncio']
if asyncio is None:
    raise SkipTest("asyncio not available")

from rx.core import Observable, Disposable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToFuture(unittest.TestCase):

    def test_future_success(self):
        loop = asyncio.get_event_loop()
        success = [False, True]

        @asyncio.coroutine
        def go():
            source = Observable.return_value(42)
            future = source.to_future(asyncio.Future)

            def done(future):
                try:
                    value = future.result()
                except Exception:
                    success[1] = False
                else:
                    success[0] = value == 42

            future.add_done_callback(done)

        loop.run_until_complete(go())
        assert(all(success))

    def test_future_failure(self):
        loop = asyncio.get_event_loop()
        success = [True, False]

        @asyncio.coroutine
        def go():
            error = Exception('woops')

            source = Observable.throw_exception(error)
            future = source.to_future(asyncio.Future)

            def done(future):
                try:
                    future.result()
                except Exception as ex:
                    success[1] = str(ex) == str(error)
                else:
                    success[0] = False

            future.add_done_callback(done)

        loop.run_until_complete(go())
        assert(all(success))

