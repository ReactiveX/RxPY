import asyncio
import unittest
from asyncio import Future

import rx


class TestFromFuture(unittest.TestCase):
    def test_future_success(self):
        loop = asyncio.get_event_loop()
        success = [False, True, False]

        async def go():
            future = Future()
            future.set_result(42)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = x == 42

            def on_error(err):
                success[1] = False

            def on_completed():
                success[2] = True

            source.subscribe(on_next, on_error, on_completed)

        loop.run_until_complete(go())
        assert all(success)

    def test_future_failure(self):
        loop = asyncio.get_event_loop()
        success = [True, False, True]

        async def go():
            error = Exception("woops")

            future = Future()
            future.set_exception(error)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = False

            def on_error(err):
                success[1] = str(err) == str(error)

            def on_completed():
                success[2] = False

            source.subscribe(on_next, on_error, on_completed)

        loop.run_until_complete(go())
        assert all(success)

    def test_future_cancel(self):
        loop = asyncio.get_event_loop()
        success = [True, False, True]

        async def go():
            future = Future()
            source = rx.from_future(future)

            def on_next(x):
                success[0] = False

            def on_error(err):
                success[1] = type(err) == asyncio.CancelledError

            def on_completed():
                success[2] = False

            source.subscribe(on_next, on_error, on_completed)
            future.cancel()

        loop.run_until_complete(go())
        assert all(success)

    def test_future_dispose(self):
        loop = asyncio.get_event_loop()
        success = [True, True, True]

        async def go():
            future = Future()
            future.set_result(42)

            source = rx.from_future(future)

            def on_next(x):
                success[0] = False

            def on_error(err):
                success[1] = False

            def on_completed():
                success[2] = False

            subscription = source.subscribe(on_next, on_error, on_completed)
            subscription.dispose()

        loop.run_until_complete(go())
        assert all(success)
