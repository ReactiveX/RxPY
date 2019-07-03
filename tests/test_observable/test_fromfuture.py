import asyncio
from asyncio import Future
import unittest

import rx


class TestFromFuture(unittest.TestCase):

    def test_future_success(self):
        loop = asyncio.get_event_loop()
        success = [False, True, False]

        @asyncio.coroutine
        def go():
            future = Future()
            future.set_result(42)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = x == 42

            def on_error(err):
                success[1] = False

            def on_completed():
                success[2] = True

            source.subscribe_(on_next, on_error, on_completed)

        loop.run_until_complete(go())
        assert(all(success))

    def test_future_failure(self):
        loop = asyncio.get_event_loop()
        success = [True, False, True]

        @asyncio.coroutine
        def go():
            error = Exception('woops')

            future = Future()
            future.set_exception(error)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = False

            def on_error(err):
                success[1] = str(err) == str(error)

            def on_completed():
                success[2] = False

            source.subscribe_(on_next, on_error, on_completed)

        loop.run_until_complete(go())
        assert all(success)

    def test_future_dispose(self):
        loop = asyncio.get_event_loop()
        success = [True, True, True]

        @asyncio.coroutine
        def go():
            future = Future()
            future.set_result(42)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = False

            def on_error(err):
                success[1] = False

            def on_completed():
                success[2] = False

            subscription = source.subscribe_(on_next, on_error, on_completed)
            subscription.dispose()

        loop.run_until_complete(go())
        assert all(success)
