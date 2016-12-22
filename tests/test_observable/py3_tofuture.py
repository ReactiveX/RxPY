
import unittest

from nose import SkipTest
import sys
if sys.version_info.major < 3:
    raise SkipTest("Py3 language async language support required")

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
    def test_await_success(self):
        loop = asyncio.get_event_loop()
        result = None

        async def go():
            nonlocal result
            source = Observable.return_value(42)
            result = await source

        loop.run_until_complete(go())
        assert(result == 42)
    def test_await_error(self):
        loop = asyncio.get_event_loop()
        error = Exception("error")
        result = None

        async def go():
            nonlocal result
            source = Observable.throw(error)
            try:
                result = await source
            except Exception as ex:
                result = ex

        loop.run_until_complete(go())
        assert(result == error)
