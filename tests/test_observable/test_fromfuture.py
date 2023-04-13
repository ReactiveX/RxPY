import asyncio
import unittest
from asyncio import Future
from typing import Any

import reactivex


class TestFromFuture(unittest.TestCase):
    def test_future_success(self):
        loop = asyncio.get_event_loop()
        success = [False, True, False]

        async def go():
            future: Future[int] = Future()
            future.set_result(42)

            source = reactivex.from_future(future)

            def on_next(x: int):
                success[0] = x == 42

            def on_error(_err: Exception):
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

            future: Future[Any] = Future()
            future.set_exception(error)

            source = reactivex.from_future(future)

            def on_next(x: Any):
                success[0] = False

            def on_error(err: Exception):
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
            future: Future[Any] = Future()
            source = reactivex.from_future(future)

            def on_next(x: Any):
                success[0] = False

            def on_error(err: Any):
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
            future: Future[int] = Future()
            future.set_result(42)

            source = reactivex.from_future(future)

            def on_next(x: int):
                success[0] = False

            def on_error(err: Exception):
                success[1] = False

            def on_completed():
                success[2] = False

            subscription = source.subscribe(on_next, on_error, on_completed)
            subscription.dispose()

        loop.run_until_complete(go())
        assert all(success)
